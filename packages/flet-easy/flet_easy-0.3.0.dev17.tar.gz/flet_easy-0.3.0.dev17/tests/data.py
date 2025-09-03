import flet as ft

import flet_easy as fs

app = fs.FletEasy()


@app.page("/", title="Test", share_data=True)
def test_page(data: fs.Datasy):
    page = data.page

    info = ft.TextField(label="info", text_size=20, text_align="center")
    content = ft.Column()
    text = ft.Text()

    data.share.set("test", [])

    def start(e):
        data.share.get("test").append(info.value)
        text.value = str(data.share.get("test"))
        content.controls.append(ft.Text(info.value))
        info.value = ""
        page.update()

    return ft.View(
        controls=[
            ft.Text("Access to shared data in web?"),
            text,
            ft.Row(
                controls=[info, ft.FilledButton("start", on_click=start, height=50)],
                alignment="center",
            ),
            content,
        ],
        horizontal_alignment="center",
        vertical_alignment="center",
    )


app.run()
