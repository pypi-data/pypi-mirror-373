import pydicom

from pynetdicom import AE
from pynetdicom.sop_class import Verification  # type: ignore

from dicom_qr.settings import PacsConfig

TRANSFER_SYNTAX = [
    pydicom.uid.ExplicitVRLittleEndian,
    pydicom.uid.ImplicitVRLittleEndian,
    pydicom.uid.DeflatedExplicitVRLittleEndian,
    pydicom.uid.ExplicitVRBigEndian,
]


def echo_scu(pacs_config: PacsConfig) -> None:
    """ Perform C-ECHO """
    application_entity = AE(ae_title=pacs_config.client_ae_title)
    application_entity.add_requested_context(Verification, TRANSFER_SYNTAX)

    assoc = application_entity.associate(pacs_config.server_ae_ip, pacs_config.server_ae_port,
                                         ae_title=pacs_config.server_ae_title)

    if not assoc.is_established:
        raise RuntimeError('Association not established.')

    status = assoc.send_c_echo()
    if not status:
        raise RuntimeError(status)

    assoc.release()
