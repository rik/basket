from optparse import make_option

from django.core.management.base import LabelCommand, CommandError
from django.core.urlresolvers import get_callable

import commonware.log

from subscriptions.models import Subscription
from utils import locked


log = commonware.log.getLogger('basket')


class Command(LabelCommand):
    """
    Unsubscribe users from a campaign.

    You may pass a function for conditionally determining whether
    a subscriber should be unsubscribed.
    """ 

    option_list = LabelCommand.option_list + (
        make_option('--conditional', '-c', dest='conditional',
                    help=('Function for determining whether a'
                          'subscriber should be unsubscribed.'
                          'This will be passed a Subscription object.')),
    )
    help = 'Unsubscribe users from a campaign.'
    args = '<campaign campaign ...>'
    label = 'campaign'

    @locked('unsubscribe')
    def handle_label(self, label, **options):
        """
        Locked command handler to avoid running this command more than once
        simultaneously.
        """

        conditional = getattr(self, 'conditional', None)
        if not conditional:
            conditional_name = options.get('conditional', None)
            if conditional_name:
                try:
                    conditional = get_callable(conditional_name)
                    log.info("Using conditional %s" % conditional_name)
                except AttributeError: 
                    raise CommandError(
                        'Conditional %s is not callable.' % conditional_name)
            else:
                conditional = lambda x: True

        try:
            targets = Subscription.objects.filter(campaign=label, active=True)
            log.info("Found %d targets" % targets.count())
            unsub_count = 0
            for target in targets:
                if conditional(target):
                    target.active = False
                    unsub_count += 1
                target.save()
            log.info("Unsubscribed %d" % unsub_count)
                     
        except Exception, e:
            raise CommandError(e)
