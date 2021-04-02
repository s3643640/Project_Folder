from django.conf import settings
from django.conf.urls.static import static
from tweet import views
from django.urls import path
from django.views.generic import TemplateView

urlpatterns=[
            path('tweets/',views.tweet_home),
            path('',views.index, name="tweets"),
            path('create/',views.Tweet_create_view, name="create"),
            path('react/', TemplateView.as_view(template_name='tweet/react_via_dj.html')),
            path('tweet/<int:tweet_id>', views.tweet_detail),
            path('api/tweet/<int:tweet_id>/delete', views.tweet_delete),
            path('api/tweet/action', views.tweet_action)

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                document_root=settings.STATIC_ROOT)
