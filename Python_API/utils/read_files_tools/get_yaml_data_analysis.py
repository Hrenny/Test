from utils.cache_control.cache_control import CacheHandler


class GetTestCase:
    @staticmethod
    def case_data(case_id_lists):
        case_lists = []
        for i in case_id_lists:
            _data = CacheHandler.get_cache(i)
            case_lists.append(_data)
        return case_lists