import os
from abc import abstractmethod

from rest_framework import status
from rest_framework.response import Response

from . import BaseView
from ..security import OAuth2Authentication, oauth2_scope_required, group_required


class ParentChildrenCRUDView(BaseView):
    authentication_classes = [] if os.getenv("ENV") == 'test' else [OAuth2Authentication]

    def __init__(self, *args, **kwargs):
        self.service = None
        super().__init__(*args, **kwargs)

    def get_serializer_context(self):
        return {
            'request': self.request,
            **super().get_serializer_context(),
        }

    @abstractmethod
    def _get_parent(self):
        pass

    @abstractmethod
    def _get_parent_or_404(self):
        pass

    @abstractmethod
    def _get_child_by_id(self, parent, pk):
        pass

    @abstractmethod
    def _create_child(self, parent, payload):
        pass

    @abstractmethod
    def _update_child(self, parent, pk, payload):
        pass

    @abstractmethod
    def _delete_child(self, parent, pk):
        pass

    @oauth2_scope_required()
    @group_required()
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = self.apply_ordering(queryset)

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @oauth2_scope_required()
    @group_required()
    def retrieve(self, request, pk=None, *args, **kwargs):
        parent = self._get_parent_or_404()
        child = self._get_child_by_id(parent, pk)
        serializer = self.get_serializer(child)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @oauth2_scope_required()
    @group_required()
    def create(self, request, *args, **kwargs):
        parent = self._get_parent_or_404()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item_child = self._create_child(parent, serializer.validated_data)
        response_serializer = self.get_serializer(item_child)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @oauth2_scope_required()
    @group_required()
    def update(self, request, pk=None, *args, **kwargs):
        parent = self._get_parent_or_404()
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        item_child = self._update_child(parent, pk, serializer.validated_data)
        response_serializer = self.get_serializer(item_child)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @oauth2_scope_required()
    @group_required()
    def destroy(self, request, pk=None, *args, **kwargs):
        parent = self._get_parent_or_404()
        self._delete_child(parent, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
