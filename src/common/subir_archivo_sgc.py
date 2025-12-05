
def subir_archivo_sgc(page, ruta_archivo):
    input_file = page.wait_for_selector('input#myfile', state='visible')
    input_file.set_input_files(ruta_archivo)
    print(f"Archivo {ruta_archivo} subido correctamente.")