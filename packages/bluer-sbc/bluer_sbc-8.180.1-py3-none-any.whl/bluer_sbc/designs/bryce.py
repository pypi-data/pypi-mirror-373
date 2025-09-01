from bluer_objects import README

image_template = "https://github.com/kamangir/assets2/blob/main/bryce/{}?raw=true"

marquee = README.Items(
    [
        {
            "name": "bryce",
            "marquee": image_template.format("08.jpg"),
            "url": "./bluer_sbc/docs/bryce.md",
        }
    ]
)

items = README.Items(
    [
        {
            "marquee": image_template.format(f"{index+1:02}.jpg"),
            "name": "",
        }
        for index in range(9)
    ]
)
