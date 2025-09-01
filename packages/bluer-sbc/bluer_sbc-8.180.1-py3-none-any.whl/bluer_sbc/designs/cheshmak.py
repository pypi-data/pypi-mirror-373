from bluer_objects import README

image_template = "https://github.com/kamangir/assets2/blob/main/cheshmak/{}?raw=true"

marquee = README.Items(
    [
        {
            "name": "cheshmak",
            "marquee": image_template.format("01.png"),
            "url": "./bluer_sbc/docs/cheshmak.md",
        }
    ]
)

items = README.Items(
    [
        {
            "marquee": image_template.format(f"{index+1:02}.png"),
            "name": "",
        }
        for index in range(1)
    ]
)
