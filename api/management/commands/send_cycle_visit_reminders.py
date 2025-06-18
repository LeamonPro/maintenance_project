# Create this file in: your_app/management/commands/send_cycle_visit_reminders.py

import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Notification
from api.models import OrdreImputation, UserProfile # Replace your_app_name
from api.views import create_notification # Replace your_app_name

class Command(BaseCommand):
    help = 'Sends reminder notifications for upcoming OrdreImputation cycle visits.'

    def handle(self, *args, **options):
        today = timezone.now().date()
        reminder_threshold_date = today + datetime.timedelta(days=10)
        
        self.stdout.write(self.style.SUCCESS(f"Checking for cycle visits due on or before {reminder_threshold_date}..."))

        # Find OrdreImputations that have a 'date_prochain_cycle_visite' set,
        # are due within the next 10 days (inclusive of today),
        # and for which a reminder hasn't been recently sent (to avoid spamming).
        # For simplicity, this example doesn't track if a reminder was already sent for this specific due date.
        # A more robust solution might involve a "last_reminder_sent_for_due_date" field or similar.
        
        ordres_due = OrdreImputation.objects.filter(
            date_prochain_cycle_visite__isnull=False,
            date_prochain_cycle_visite__lte=reminder_threshold_date,
            date_prochain_cycle_visite__gte=today # Only future or today's visits
        )

        if not ordres_due.exists():
            self.stdout.write(self.style.SUCCESS("No cycle visits due for reminders at this time."))
            return

        chefs_de_parc_profiles = UserProfile.objects.filter(role='Chef de Parc')
        if not chefs_de_parc_profiles.exists():
            self.stdout.write(self.style.WARNING("No 'Chef de Parc' users found to send notifications to."))
            return

        notifications_sent_count = 0
        for ordre in ordres_due:
            self.stdout.write(f"Processing OI: {ordre.value}, Due: {ordre.date_prochain_cycle_visite}")
            
            # Check if a notification for this OI and this specific due date was already sent to Chefs de Parc
            # This is a simple check; a more complex system might be needed for perfect idempotency
            existing_reminder = Notification.objects.filter(
                ordre_imputation_related=ordre,
                notification_category='CYCLE_VISIT',
                message__icontains=f"Le cycle de visite pour l'OI '{ordre.value}' est prévu pour le {ordre.date_prochain_cycle_visite.strftime('%d/%m/%Y')}"
            ).filter(
                recipient_role='Chef de Parc' # Check for role-based notification
            ).exists()

            if existing_reminder:
                self.stdout.write(self.style.NOTICE(f"Reminder already sent for OI {ordre.value} due on {ordre.date_prochain_cycle_visite}."))
                continue


            message = f"Rappel: Le cycle de visite pour l'OI '{ordre.value}' est prévu pour le {ordre.date_prochain_cycle_visite.strftime('%d/%m/%Y')}. Veuillez enregistrer le résultat après la visite."
            
            for chef_profile in chefs_de_parc_profiles:
                if chef_profile.user:
                    create_notification(
                        message=message,
                        recipient_type='UserInRole', # Or 'Role' if you want one notification per role
                        recipient_role='Chef de Parc',
                        recipient_user_id=chef_profile.user.id, # Send to each Chef de Parc
                        notification_category='CYCLE_VISIT',
                        ordre_imputation_id=ordre.id_ordre
                    )
                    notifications_sent_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  Notification sent to {chef_profile.name} for OI {ordre.value}"))
            
            # If sending one notification per role instead of per user:
            # create_notification(
            #     message=message,
            #     recipient_type='Role',
            #     recipient_role='Chef de Parc',
            #     notification_category='CYCLE_VISIT',
            #     ordre_imputation_id=ordre.id_ordre
            # )
            # notifications_sent_count += 1 # Count as one for the role
            # self.stdout.write(self.style.SUCCESS(f"  Role-based notification sent for OI {ordre.value}"))


        self.stdout.write(self.style.SUCCESS(f"Finished sending reminders. Total notifications sent in this run: {notifications_sent_count}"))
