
import platform

if platform.system() == "Windows":
    import win32com.client  


def close_excel_worksheet(filename, save=True):
    """
    Fecha um arquivo específico do Excel no Windows.
    :param arquivo: Nome do arquivo aberto no Excel (ex: 'Planilha1.xlsx')
    :param salvar: Se True, salva as alterações antes de fechar
    """
    
    try:
        
        if platform.system() != "Windows":
            print("Esta função só está disponível no Windows.")
            return
        
        excel = win32com.client.Dispatch("Excel.Application")
        for wb in excel.Workbooks:
            if wb.Name.lower() == filename.lower():  # compara ignorando maiúsc/minúsc
                if save:
                    wb.Close(SaveChanges=1)  # 1 = salvar alterações
                    print(f"O arquivo {filename} foi salvo e fechado com sucesso no Windows.")
                else:
                    wb.Close(SaveChanges=0)  # 0 = fechar sem salvar
                    print(f"O arquivo {filename} foi fechado sem salvar no Windows.")
                return
        print(f"O arquivo {filename} não estava aberto no Excel.")
    except Exception as e:
        print(f"Erro ao tentar fechar {filename} no Windows: {e}")

