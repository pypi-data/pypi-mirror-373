from django.urls import path

from .channels.views import handel_channel
from .views import rest, meta, file

urlpatterns = [
    path('socket/<str:handler>', handel_channel),
    path('batch', rest.batch),
    path('<str:db>/<str:entity>/save_one', rest.save_one),
    path('<str:db>/<str:entity>/delete_one', rest.delete_one),
    path('<str:db>/<str:entity>/find_one', rest.find_one),
    path('<str:db>/<str:entity>/find', rest.find),
    path('<str:db>/<str:entity>/update', rest.update),
    path('<str:db>/<str:entity>/search', rest.search),
    path('<str:db>/<str:entity>/values', rest.values),
    # path('<str:db>/<str:entity>/tree', rest.tree),

    path('<str:db>/<str:entity>/meta_view', meta.meta_view),
    path('metas', meta.metas),
    path('add_fields', meta.add_fields),
    path('load_customs', meta.load_customs),
    path('get_fields', meta.get_fields),
    path('save_custom', meta.save_custom),
    path('upload_mapping', meta.upload_mapping),

    path('<str:db>/<str:entity>/save_file', file.save_file),
    path('<str:db>/<str:entity>/remove_file', file.remove_file),

]
