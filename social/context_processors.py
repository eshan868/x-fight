from .models import Notification

def notifications(request):

    
    if request.user.is_authenticated:

        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")
        
        for notification in notifications:
            print(notification.text)

        return {
            "notifications": notifications,
            "notification_count": notifications.filter(is_read=False).count()
        }

    return {
        "notifications": [],
        "notification_count": 0
    }