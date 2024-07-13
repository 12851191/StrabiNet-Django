from django.db import models

class UploadedImage(models.Model):
    user_id = models.CharField(max_length=255)
    face_image = models.CharField(max_length=255, blank=True, null=True)
    left_eye_image = models.CharField(max_length=255, blank=True, null=True)
    right_eye_image = models.CharField(max_length=255, blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
