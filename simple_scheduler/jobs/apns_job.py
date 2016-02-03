"""Simple job to send test Apple Push Notifications."""

import logging

from ndscheduler import job
from apns import APNs, Payload

logger = logging.getLogger(__name__)


class APNSJob(job.JobBase):
    TIMEOUT = 10

    @classmethod
    def meta_info(cls):
        return {
            'job_class_string': '%s.%s' % (cls.__module__, cls.__name__),
            'notes': 'This sends a push notification to APNS servers',
            'arguments': [
                # APNS device token
                {'token': 'string', 'description': 'Device token'},
                # APNS Title's Alert Text
                {'alert': 'string', 'description': 'What do you want to send?'},
            ],
            'example_arguments': ('["da1232badh2", "Hello from scheduler"]')
        }

    def run(self, token, alert="Hello World",  *args, **kwargs):
        print 'Sending %s to %s' % (alert, token)

        apns = APNs(use_sandbox=False, cert_file='simple_scheduler/jobs/apns-cert.pem')
        # Send a notification
        payload = Payload(alert=alert, sound="default", badge=0)
        apns.gateway_server.send_notification(token, payload)


if __name__ == "__main__":
    job = APNSJob.create_test_instance()
    job.run('da1232badh2', 'Hello World')
