from django.urls import path
from . import views

# Create your urls here.
urlpatterns = [
    path("merge/", views.merge_pdfs_view),
    path("compress/", views.compress_view),
    path("jpg-to-pdf/", views.images_to_pdf_view),
    path("pdf-to-images/", views.pdf_to_images_view),
    path("office-to-pdf/", views.oofice_to_pdf_view),
]