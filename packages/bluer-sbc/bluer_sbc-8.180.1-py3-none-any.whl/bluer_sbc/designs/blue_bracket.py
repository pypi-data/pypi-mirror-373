from bluer_objects import README

design_template = "https://github.com/kamangir/blue-bracket/blob/main/designs/{}.md"

image_template = "https://github.com/kamangir/blue-bracket/raw/main/images/{}"

items = README.Items(
    [
        {
            "name": item["name"],
            "marquee": image_template.format(item["image"]),
            "url": design_template.format(item["name"]),
        }
        for item in [
            {
                "image": "blue3-1.jpg",
                "name": "blue3",
            },
            {
                "image": "chenar-grove-1.jpg",
                "name": "chenar-grove",
            },
            {
                "image": "cube-1.jpg",
                "name": "cube",
            },
            {
                "image": "eye_nano-1.jpg",
                "name": "eye_nano",
            },
        ]
    ]
)
