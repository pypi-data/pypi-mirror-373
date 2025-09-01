import datetime, uuid, logging

from typing import Dict, List, Optional, Union

from etiket_client.local.dao.dataset import dao_dataset
from etiket_client.local.models.dataset import DatasetSearch as DatasetSearchLocal
from etiket_client.remote.authenticate import validate_login_status
from etiket_client.remote.endpoints.models.dataset import DatasetSearch as DatasetSearchRemote
from etiket_client.remote.errors import CONNECTION_ERRORS
from etiket_client.local.models.scope import ScopeReadWithUsers
from etiket_client.python_api.scopes import get_scope_by_name, get_scope_by_uuid, get_selected_scope
from etiket_client.remote.endpoints.dataset import dataset_search
from etiket_client.local.database import Session
from qdrive.dataset.dataset import dataset

logger = logging.getLogger(__name__)

def search_datasets(
    search_query: Optional[str] = None,
    attributes: Optional[Dict[str, Union[str, int, float, List]]] = None,
    ranking: int = 0,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    scopes: Optional[List[Union[str, uuid.UUID, ScopeReadWithUsers]]] = None,
) -> "SearchResult":
    """
    Perform a search for datasets based on the provided criteria.

    Args:
        search_query (Optional[str]): The search query string to filter datasets.
        attributes (Optional[Dict[str, Union[str, int, float]]]): Additional attributes to filter datasets.
        ranking (int): The ranking score to filter datasets. Defaults to 0.
        start_date (Optional[datetime.datetime]): The start date to filter datasets.
        end_date (Optional[datetime.datetime]): The end date to filter datasets.
        scopes (Optional[List[Union[str, uuid.UUID, ScopeReadWithUsers]]]): A list of scopes to filter datasets. Each scope can be a name (str), UUID (uuid.UUID), or a ScopeReadWithUsers object.

    Returns:
        SearchResult: An instance of the SearchResult class containing the search results.
    """
    validate_login_status()
    return SearchResult(
        search_query=search_query,
        attributes=attributes,
        ranking=ranking,
        start_date=start_date,
        end_date=end_date,
        scopes=scopes
    )

class SearchResult:
    '''
    This is class that holds the results of the search, but the search is paginated.
    '''
    def __init__(
        self,
        search_query: Optional[str] = None,
        attributes: Optional[Dict[str, Union[str, int, float, List]]] = None,
        ranking: int = 0,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        scopes: Optional[List[Union[str, uuid.UUID, ScopeReadWithUsers]]] = None,
    ):
        """
        Initialize a SearchResult instance.

        Args:
            search_query (Optional[str]): The search query string to filter datasets.
            attributes (Optional[Dict[str, Union[str, int, float]]]): Additional attributes to filter datasets.
            ranking (int): The ranking score to filter datasets. Defaults to 0.
            start_date (Optional[datetime.datetime]): The start date to filter datasets.
            end_date (Optional[datetime.datetime]): The end date to filter datasets.
            scopes (Optional[List[Union[str, uuid.UUID, ScopeReadWithUsers]]]): A list of scopes to filter datasets. Each scope can be a name (str), UUID (uuid.UUID), or a ScopeReadWithUsers object.

        Raises:
            TypeError: If any of the provided scopes are of an invalid type.
        """
        self._index: int = 0
        self._limit: int = 40
        self._offset: int = 0
        self._finished: bool = False
        self._session = Session()
        self._result_cache_local: List = []
        self._result_cache_remote: List = []
        self._results: List = []
        
        self.scope_to_search = self._resolve_scope_uuids(scopes)
                
        self.local_search_query = DatasetSearchLocal(scope_uuids=[scope.uuid for scope in self.scope_to_search],
                                                        search_query=search_query,
                                                        attributes=format_attributes(attributes),
                                                        ranking=ranking,
                                                        start_date=start_date,
                                                        end_date=end_date)
        self.remote_search_query = DatasetSearchRemote(scope_uuids=[scope.uuid for scope in self.scope_to_search],
                                                        search_query=search_query,
                                                        attributes=format_attributes(attributes),
                                                        ranking=ranking,
                                                        start_date=start_date,
                                                        end_date=end_date)
    @property
    def first(self) -> dataset:
        '''
        Get the first result.

        Returns:
            dataset: The first dataset in the search results.

        Raises:
            ValueError: If no results are found.
        '''
        if len(self._results) == 0:
            self._get_new_results()
            
        if len(self._results) > 0:
            return self._results[0]
        raise ValueError("No results found.")
    
    def __iter__(self):
        '''
        Return an iterator over the search results.

        Returns:
            SearchResult: The iterator instance.
        '''
        self._index = 0
        return self

    def __next__(self) -> dataset:
        '''
        Return the next dataset in the search results.

        Returns:
            dataset: The next dataset in the search results.

        Raises:
            StopIteration: If there are no more results.
        '''
        if self._index == len(self._results):
            self._get_new_results()
            
        if self._index < len(self._results):
            self._index += 1
            return self._results[self._index - 1]
        else:
            raise StopIteration
    
    def __repr__(self) -> str:
        """
        Return a string representation of the SearchResult instance.

        Returns:
            str: A string representation of the SearchResult instance.
        """
        options = []
        if self.local_search_query.search_query:
            options.append(f"- search_query: {self.local_search_query.search_query}")
        if self.local_search_query.attributes:
            attributes_str = "- attributes:"
            for key, value in self.local_search_query.attributes.items():
                if isinstance(value, list):
                    value_str = " or ".join(value)
                else:
                    value_str = str(value)
                attributes_str += f"\n\t* {key}: {value_str}"
            options.append(attributes_str)
        if self.local_search_query.ranking != 0:
            options.append(f"- ranking: {self.local_search_query.ranking}")
        if self.local_search_query.start_date:
            options.append(f"- start_date: {self.local_search_query.start_date}")
        if self.local_search_query.end_date:
            options.append(f"- end_date: {self.local_search_query.end_date}")
        if self.local_search_query.scope_uuids:
            scope_names = [scope.name for scope in self.scope_to_search]
            options.append(f"- scopes: {', '.join(scope_names)}")

        return "SearchResult with the following parameters:\n" + "\n".join(options)
        
    def _get_new_results(self) -> Optional[List[dataset]]:
        '''
        Fetch the next page of results from local and remote sources.
        '''
        if self._finished is True:
            return
        res_local = dao_dataset.search(self.local_search_query, self._session, self._offset, self._limit)
        try:
            res_rem = dataset_search(self.remote_search_query, self._offset, self._limit)
        except CONNECTION_ERRORS as e:
            logger.warning(f"Remote search failed: {e}")
            print("Warning: Only performing local search (remote search failed).")
            res_rem = []
        
        self._result_cache_local += res_local
        self._result_cache_remote += res_rem
        
        no_new_results = False
        
        if len(res_local) < self._limit and len(res_rem) < self._limit:
            no_new_results = True
        
        self._merge_results(no_new_results)
        self._offset += self._limit
        self._finished = no_new_results
        return self._results

    def _merge_results(self, merge_all=False) -> None:
        '''
        Merge local and remote search results, removing duplicates.

        Args:
            merge_all (bool): If True, merge all results. If False, merge up to the current limit.
        '''
        merged_results = {}

        for item in self._result_cache_local:
            if item.uuid in merged_results:
                merged_results[item.uuid]['local'] = item
            else:
                merged_results[item.uuid] = {'local': item, 'remote': None}

        for item in self._result_cache_remote:
            if item.uuid in merged_results:
                merged_results[item.uuid]['remote'] = item
            else:
                merged_results[item.uuid] = {'local': None, 'remote': item}

        merged_list = list(merged_results.values())

        merged_list.sort(key=lambda x: (
            x['local'].collected if x['local'] else x['remote'].collected
        ), reverse=True)

        if not merge_all:
            merged_list = merged_list[:self._limit]

        for item in merged_list:
            self._results.append(dataset.init_raw(item['local'], item['remote']))

        processed_local_uuids = {item['local'].uuid for item in merged_list if item['local']}
        processed_remote_uuids = {item['remote'].uuid for item in merged_list if item['remote']}
        self._result_cache_local = [item for item in self._result_cache_local if item.uuid not in processed_local_uuids]
        self._result_cache_remote = [item for item in self._result_cache_remote if item.uuid not in processed_remote_uuids]
    
    def _resolve_scope_uuids(self, scopes : Optional[List[Union[str, uuid.UUID, ScopeReadWithUsers]]]) -> List[ScopeReadWithUsers]:
        """
        Resolve scopes to their UUIDs.

        Args:
            scopes (Optional[List[Union[str, uuid.UUID, ScopeReadWithUsers]]]): List of scopes.

        Returns:
            List[ScopeReadWithUsers]: List of scope UUIDs.

        Raises:
            TypeError: If a scope is of an invalid type.
            ValueError: If a scope name does not correspond to any existing scope.
        """
        scope_to_search = []
        if scopes is None:
            scope_to_search.append(get_selected_scope())
        else:
            for scope in scopes:
                if isinstance(scope, ScopeReadWithUsers):
                    scope_to_search.append(scope)
                elif isinstance(scope, str):
                    scope_to_search.append(get_scope_by_name(scope))
                elif isinstance(scope, uuid.UUID):
                    scope_to_search.append(get_scope_by_uuid(scope))
                else:
                    raise TypeError(f"Invalid type for scope ({type(scope)}).")
        return scope_to_search

def format_attributes(attributes : Optional[Dict[str, Union[str, int, float, List]]]) -> Optional[Dict[str, List[str]]]:
    """
    Format attributes for search.

    Args:
        attributes (Dict[str, Union[str, int, float]): Dictionary of attributes.

    Returns:
        Dict[str, List[str]]: Formatted attributes.
    """
    if attributes is None:
        return None

    formatted_attributes = {}
    for key, value in attributes.items():
        if isinstance(value, list):
            formatted_attributes[key] = [str(item) for item in value]
        else:
            formatted_attributes[key] = [str(value)]
    
    return formatted_attributes
