from django.utils.translation import gettext_lazy as _

from mayan.apps.dependencies.classes import BinaryDependency

from .drivers import ClamScanDriver

clamscan = ClamScanDriver(auto_initialize=False)
clamscan.read_settings()

BinaryDependency(
    help_text=_(message='Command line anti-virus scanner.'), module=__name__,
    name='clamscan', path=clamscan.path_clamscan
)
