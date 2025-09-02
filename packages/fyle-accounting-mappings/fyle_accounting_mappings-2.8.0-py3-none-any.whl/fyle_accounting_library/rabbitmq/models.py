from django.db import models


class FailedEvent(models.Model):
    """
    Model to store the failed events
    """
    id = models.AutoField(primary_key=True, help_text='Primary key for the failed event')
    routing_key = models.CharField(max_length=255, help_text='RabbitMQ routing key for the failed event')
    payload = models.JSONField(default=dict, help_text='JSON payload of the failed event')
    created_at = models.DateTimeField(auto_now_add=True, help_text='Timestamp when the failed event was created')
    updated_at = models.DateTimeField(auto_now=True, help_text='Timestamp when the failed event was last updated')
    error_traceback = models.TextField(null=True, help_text='Error traceback from the failed event')
    workspace_id = models.IntegerField(null=True, help_text='Reference to the workspace where this event occurred')
    is_resolved = models.BooleanField(default=False, help_text='Whether the failed event has been resolved')

    class Meta:
        db_table = 'failed_events'
        app_label = 'rabbitmq'
