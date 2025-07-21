from pywebpush import webpush, WebPushException
from app import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_CLAIMS,DB_INIT
import json


class ManageNotifications:
    
    # App Notifications Blueprint 
    def app_notification(recipient_sub,curr_user,msg,title="Q-Messanger",url="/"):

        recipient_sub_info = {
                "endpoint": recipient_sub.endpoint,
                "keys": {
                    "p256dh": recipient_sub.p256dh,
                    "auth": recipient_sub.auth
                }
            }
        try:
            print(f"Updates! {curr_user}")
            webpush(
                recipient_sub_info,
                data=json.dumps({
                    "title": title,
                    "body": msg,
                    "url": url if url else "https://qm.techxolutions.com",
                    "username": curr_user
                }),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS,
                ttl=200
            )
            print("Web Push Activated, Update!")

        except WebPushException as ex:
            if '410' in str(ex) or 'unsubscribed or expired' in str(ex):
                # Remove subscription from DB_INIT
                DB_INIT.session.delete(recipient_sub)
                DB_INIT.session.commit()
                print(f"Removed expired subscription uid: {recipient_sub.usr_id}")
            else:
                print("Web push failed, update: {}", repr(ex))