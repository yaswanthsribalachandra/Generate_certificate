from pydantic import BaseModel


class Applicant(BaseModel):

    sl_no: str
    application_id: str
    name: str
    father_name: str
    date_of_birth: str
    age: str
    place_of_birth: str
    present_residing_at: str
    address_part_1: str
    address_part_2: str
    nationality: str
    work_in_state: str
    height: str
    identification_mark_1: str
    identification_mark_2: str
    mobile_no: str
    certificate_class: str
    challan_no: str
    challan_date: str
    amount: str
    payment_status: str
    file_no: str
    status: str
    reason: str
    exam_date: str
    result: str