from django.conf.urls import url,include
import settings
#from django.views.static import serve

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Example:
    # (r'^autoradio/', include('autoradio.foo.urls')),

#    (r'^xmms/', include('programs.urls')),
#    (r'^$', include('spots.urls')),
#    (r'^$', include('jingles.urls')),

#    Uncomment the next line to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

#    Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('pyonenet.onenet.urls')),
#    url(r'^', include('pyonenet.oncron.urls')),
]

#if ( settings.SERVE_STATIC ):
##serve local static files
#    urlpatterns += patterns('',
#                            (r'^'+settings.SITE_MEDIA_PREFIX[1:]+'(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_SITE_ROOT, 'show_indexes': True}),
#                            (r'^'+settings.MEDIA_PREFIX[1:]+'(.*)', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
#                            )
