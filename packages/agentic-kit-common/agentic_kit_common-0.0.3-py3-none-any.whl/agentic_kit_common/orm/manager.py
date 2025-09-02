import time
from abc import abstractmethod
from sqlalchemy import asc, desc

from .session import get_db_session


class BaseOrmManager(object):
    """Model orm manager"""

    _model_cls = None

    @classmethod
    def get_by_id(cls, obj_id, close_session_after_curd=False):
        with get_db_session() as db:
            query = db.query(cls._model_cls) \
                .filter(cls._model_cls.id == obj_id) \
                .filter(cls._model_cls.active == True)

            if hasattr(cls._model_cls, 'active'):
                query = query.filter(cls._model_cls.active == 1)

            _obj = query.first()

            if close_session_after_curd:
                db.close()

            return _obj or None

    @classmethod
    def get_object_or_none(cls, close_session_after_curd=False, **lookup):
        """Get object using lookup parameters, i.e pk=1"""
        if lookup:
            with get_db_session() as db:
                res = db.query(cls._model_cls).filter_by(**lookup).first()

                if close_session_after_curd:
                    db.close()

                return res

    @classmethod
    def get_objects_all(cls, close_session_after_curd=False, **lookup):
        if lookup:
            with get_db_session() as db:
                res = db.query(cls._model_cls).filter_by(**lookup).all()

                if close_session_after_curd:
                    db.close()

                return res

    @classmethod
    def get_list(cls, paginate=False, close_session_after_curd=False, **kwargs):
        with get_db_session() as db:
            query = db.query(cls._model_cls)
            # """分页查询示例"""
            # # 填充具体查询条件
            for column, value in kwargs.items():
                if not hasattr(cls._model_cls, column):
                    continue
                # 根据值类型，来组装查询条件
                if isinstance(value, tuple):
                    # 范围查询
                    query = query.filter(getattr(cls._model_cls, column).between(*value))
                elif isinstance(value, list):
                    # in查询
                    query = query.filter(getattr(cls._model_cls, column).in_(value))
                elif isinstance(value, str) and value.find("%") != -1:
                    # 模糊查询
                    query = query.filter(getattr(cls._model_cls, column).like(value))
                else:
                    # 等值查询
                    query = query.filter(getattr(cls._model_cls, column) == value)

            if kwargs.get('active', None) is None and hasattr(cls._model_cls, 'active'):
                query = query.filter(cls._model_cls.active == 1)

            if paginate:
                # 总数
                total = query.count()

                # 计算分页offset
                page = kwargs.get('page', 1)
                per_page = kwargs.get('per_page', 20)
                offset = (page - 1) * per_page

                # 排序
                if hasattr(cls._model_cls, 'sort'):
                    query = query.order_by(asc(cls._model_cls.sort))
                query = query.order_by(desc(cls._model_cls.id)).offset(offset).limit(per_page)

                # 查询记录
                result = query.all()
                pagination = {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'items': result
                }
                res = pagination
                # return pagination
            else:
                res = query.all()
                # return res

            if close_session_after_curd:
                db.close()

            return res

    @classmethod
    def create_obj(cls, commit=False, **kwargs):
        now = int(time.time())
        obj = cls._model_cls.create(commit=commit, created_at=now, updated_at=now, active=True, **kwargs)
        return obj

    @classmethod
    def update_obj(cls, obj, commit=False, **kwargs):
        """更新obj信息"""
        obj.update(commit=commit, updated_at=int(time.time()), **kwargs)
        return obj

    @classmethod
    def soft_delete_obj(cls, obj):
        """软删除obj信息"""
        cls.update_obj(obj, **{
            'active': False
        })
        return obj

    @classmethod
    def delete_obj(cls, obj, commit=False):
        """删除obj信息"""
        obj.delete(commit=commit)
        return obj

    @classmethod
    @abstractmethod
    def render(cls, obj):
        raise NotImplemented()

    @classmethod
    def render_simple(cls, obj):
        cls.render(obj)
