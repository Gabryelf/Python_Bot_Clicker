import flet as ft
import asyncio

DATABASE_PATH = 'database.db'
user_id = 0
url_ref = "CookiesClickerGameBot"


async def main(page: ft.Page) -> None:
    init_db()
    page.bgcolor = "#000000"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.fonts = {"appetite-italic": "https://raw.githubusercontent.com/google/fonts/master/ofl/kanit/Kanit-Bold.ttf"}
    page.theme = ft.Theme(font_family="appetite-italic")
    user_id_holder = {"value": 0}  # Создаем словарь для хранения значения user_id

    user_id_input = ft.TextField(label="Enter your user ID", autofocus=True)
    submit_button = ft.TextButton(text="Submit")

    # Создание переменной счета и текстового элемента для отображения счета
    score_text = ft.Text(value="", size=20, color="#ffb700")
    energy_text = ft.Text(value="", size=15, color="#00FFFF")

    async def restore_energy():
        while True:
            await asyncio.sleep(40)  # Ждем 40 секунд
            # Восстановление 1 единицы энергии
            for user_id in get_all_user_ids():  # Получаем все ID пользователей
                score, energy = get_game_data(user_id)
                energy += 1  # Увеличиваем энергию на 1
                if energy > 50:  # Если энергия превышает максимальное значение, устанавливаем ее равной максимальному значению
                    energy = 50
                update_game_data(user_id, score, energy)  # Обновляем данные игры в базе данных

    async def submit_click(event):
        user_id = int(user_id_input.value)  # Обновляем user_id с новым значением из поля ввода
        user_id_holder["value"] = user_id  # Сохраняем новое значение user_id
        # Используем user_id для получения данных игры из базы данных
        score, energy = get_game_data(user_id)
        print("Score:", score, "Energy:", energy)  # Отладочное сообщение
        score_text.value = f"Score: {score}"
        energy_text.value = f"Energy: {energy}"

        # Удаляем элементы ввода user_id и кнопку "Submit"
        page.remove(user_id_input)
        page.remove(submit_button)

        # Добавляем текстовые элементы на страницу
        page.add(score_text, energy_text)

        # Обновляем страницу с новыми данными
        await page.update()

    submit_button.on_click = submit_click

    # Добавляем элементы ввода на страницу
    page.add(user_id_input, submit_button)

    async def handle_click(event: ft.ContainerTapEvent) -> None:
        nonlocal score_text, energy_text
        user_id = user_id_holder["value"]
        score, energy = get_game_data(user_id)
        if energy > 0:
            score += 0.02
            energy -= 1

            score_text.value = "{:.2f}".format(score)
            energy_text.value = f"Energy: {energy}"
            energy_progress_bar_fg.width = 250 * (energy / 50)

            await page.update_async()
            await asyncio.sleep(0.1)
            clickable_image.scale = 0.95
            await page.update_async()
            await asyncio.sleep(0.1)
            clickable_image.scale = 1.0
            await page.update_async()

            # Обновление данных игры в базе данных
            update_game_data(user_id, score, energy)
            print("Score updated to:", score, "Energy updated to:", energy)  # Отладочное сообщение

            # Обновляем страницу после каждого клика
            await page.update()

    async def handle_ref_button(event: ft.TapEvent) -> None:
        # Предполагаем, что user_id_holder уже содержит user_id текущего пользователя
        ref_link = f"https://t.me/{url_ref}?start={user_id_holder['value']}"
        print("Referral link:", ref_link)  # Выводим ссылку в консоль

        # Создаем текстовый элемент для отображения реферальной ссылки
        ref_link_text = ft.Text(value=ref_link, selectable=True)

        # Создаем функцию для удаления элементов
        async def remove_elements(event: ft.TapEvent):
            page.remove(stack)  # Удаляем Stack из списка контролов страницы
            await page.update()

        # Создаем кнопку, которая будет удалять текстовый элемент и саму себя
        remove_button = ft.TextButton(text="Remove", on_click=remove_elements)

        # Группируем текстовый элемент и кнопку в строку для выравнивания
        remove_button_row = ft.Row(controls=[remove_button], alignment=ft.MainAxisAlignment.CENTER)

        # Создаем контейнер для текста и кнопки с белым фоном
        container = ft.Container(
            content=ft.Column(controls=[ref_link_text, remove_button_row], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.colors.WHITE,
            border_radius=10
        )

        # Создаем Stack, который будет содержать контейнер
        stack = ft.Stack(controls=[container])

        # Добавляем Stack на страницу
        page.add(stack)
        await page.update()

    async def show_leaderboard(event: ft.TapEvent) -> None:
        top_users = await get_top_users(10)  # Ожидаем результат выполнения асинхронной функции
        user_score_texts = [ft.Text(value=f"User ID: {user_id}, Score: {score:.2g}", color=ft.colors.WHITE) for user_id, score in top_users]

        async def close_leaderboard(event: ft.TapEvent) -> None:
            page.remove(stack)  # Удаляем Stack из списка контролов страницы
            await page.update()

        # Создаем контейнер для отображения списка пользователей и их баллов
        leaderboard_container = ft.Container(
            content=ft.Column(controls=user_score_texts, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.colors.BLACK,
            border_radius=10
        )

        # Создаем кнопку для закрытия лидерборда
        close_button = ft.TextButton(text="Close", on_click=close_leaderboard)

        # Группируем контейнер и кнопку в столбец
        container_with_close_button = ft.Column(controls=[leaderboard_container, close_button])

        # Создаем Stack для отображения контейнера с лидербордом и кнопкой "Close"
        stack = ft.Stack(controls=[container_with_close_button])

        # Добавляем Stack на страницу
        page.add(stack)
        await page.update()

    score, energy = get_game_data(user_id)
    score_text.value = "{:.2f}".format(score)
    energy_text.value = f"Energy: {energy}"

    leaderboard_button = ft.TextButton(text="Leaderboard", on_click=show_leaderboard)
    ref_button = ft.TextButton(text="Referral Link", on_click=handle_ref_button)

    buttons_row = ft.Row(controls=[leaderboard_button, ref_button], alignment=ft.MainAxisAlignment.CENTER)

    page.add(buttons_row)

    # Создание переменной энергии и текстового элемента для отображения энергии
    energy_text = ft.Text(value=f"Energy: {energy}", size=15, color="#00FFFF")

    energy_progress_bar_bg = ft.Container(
        height=10,
        width=250,
        bgcolor="#000000",
        margin=ft.Margin(top=30, right=0, left=15, bottom=-20)  # Сдвигаем влево на 50 пикселей
    )

    # Создание передней полосы прогресса для энергии
    energy_progress_bar_fg = ft.Container(
        height=10,
        width=250 * (energy / 50),
        bgcolor="#FFFF00",
        margin=ft.Margin(top=30, right=0, left=15, bottom=-20),  # Сдвигаем влево на 50 пикселей

    )

    # Создание стека для наложения полос прогресса
    progress_bar_stack = ft.Stack(controls=[energy_progress_bar_bg, energy_progress_bar_fg])

    # Clickable image
    clickable_image = ft.Image(src="cookies.png", fit=ft.ImageFit.CONTAIN, width=300, height=300)
    image_container = ft.Container(content=clickable_image, on_click=handle_click, margin=ft.Margin(top=50, right=0, left=0, bottom=0))
    page.add(image_container)

    # Создание контейнера для полос прогресса с ограничением максимальной ширины
    progress_bar_container = ft.Container(
        content=ft.Stack(controls=[energy_progress_bar_bg, energy_progress_bar_fg]),

        margin=ft.Margin(top=0, left=0, bottom=0, right=0),
        # Максимальная ширина контейнера

    )

    # Создание колонки для вертикального выравнивания элементов
    column = ft.Column(
        controls=[progress_bar_stack],
        expand=True,
    )

    # Размещение колонки на странице
    page.add(column)


    # Additional elements such as buttons, leaderboard, and referral link are already added

    # Сохраняем переменные как атрибуты объекта страницы, чтобы они оставались доступными после первого клика
    page.clickable_image = clickable_image
    page.energy_progress_bar_fg = energy_progress_bar_fg

    asyncio.create_task(restore_energy())

if __name__ == "__main__":
    ft.app(target=main, view=None, port=3001)
    #ft.app(target=main, view=ft.WEB_BROWSER)
