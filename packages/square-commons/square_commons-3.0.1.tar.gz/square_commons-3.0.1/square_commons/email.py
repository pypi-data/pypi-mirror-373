from square_commons.api_utils import make_request_json_output


def send_email_using_mailgun(
    from_email,
    from_name,
    to_email,
    to_name,
    subject,
    body,
    api_key,
    domain_name,
):

    data = {
        "from": f"{from_name} <{from_email}>",
        "to": f"{to_name} <{to_email}>",
        "subject": subject,
        "text": body,
    }

    result = make_request_json_output(
        method="POST",
        base_url="https://api.mailgun.net",
        endpoint=f"v3/{domain_name}/messages",
        auth=("api", api_key),
        data=data,
    )
    return result
