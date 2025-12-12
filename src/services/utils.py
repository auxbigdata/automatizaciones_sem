def subir_facturacion(page, URL, tercero):
    URL_MENU = f"{URL}/emsa_subir_facturacion.php"
    page.goto(URL_MENU)

    select = page.locator("select#tercero")  # o "select#id_del_select" si tiene ID

    select.select_option(
        label=tercero
    )