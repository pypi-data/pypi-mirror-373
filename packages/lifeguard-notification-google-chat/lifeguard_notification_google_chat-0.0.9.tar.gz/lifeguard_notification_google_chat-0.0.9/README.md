# lifeguard-notification-google-chat
Google Chat Notifications

## Usage

```python
@validation(
    "Description",
    actions=[notify_in_single_message],
    schedule={"every": {"minutes": 1}},
    settings={
        "notification": {
            "template": "jinja2 string template"
            "google": {
                "rooms": ["spacewebhookurl"],
            }
        },
    },
)
def a_validation():
    return ValidationResponse("a_validation", NORMAL, {}, {"notification": {"notify": True}})
```

Screenshot with output of the example found in [https://github.com/LifeguardSystem/lifeguard-example/blob/main/validations/on_error_validation.py](https://github.com/LifeguardSystem/lifeguard-example/blob/main/validations/on_error_validation.py):

![screenshot example](./docs/example-error-openai.png)

