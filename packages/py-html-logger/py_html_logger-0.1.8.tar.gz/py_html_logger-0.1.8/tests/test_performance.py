# simple_test.py - Teste básico para verificar funcionamento
import sys
import os
import time

# Para testar localmente, simula import da lib
try:
    # Se estiver rodando do diretório da lib
    from loghtml import log, info, debug, warning, error, config, flush
except ImportError:
    print("Erro: não conseguiu importar htmllogger")
    print("Certifique-se que está no diretório correto")
    sys.exit(1)


def test_basic_functionality():
    """Teste básico de funcionalidade"""
    print("🧪 Testando funcionalidade básica...")

    try:
        # Configura para teste
        config(
            log_dir="test_logs",
            main_filename="test.html",
            max_files=3
        )

        # Teste básico de logs
        print("📝 Criando logs básicos...")
        info("Teste iniciado", tag="test")
        log("Log normal", color="cyan", tag="normal")
        debug("Debug info", tag="debug")
        warning("Aviso de teste", tag="warning")
        error("Erro simulado", tag="error")

        # Força flush
        flush()

        print("✅ Logs básicos criados com sucesso!")

        # Verifica se arquivo foi criado
        log_file = os.path.join("test_logs", "test.html")
        if os.path.exists(log_file):
            file_size = os.path.getsize(log_file)
            print(f"📄 Arquivo criado: {log_file} ({file_size} bytes)")

            # Verifica conteúdo básico
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()

            if "data-tags=" in content:
                print("🏷️ Tags encontradas no HTML ✅")
            else:
                print("❌ Tags não encontradas no HTML")

            if "<!-- LOG_CONTENT -->" in content:
                print("📌 Marcador de conteúdo encontrado ✅")
            else:
                print("❌ Marcador de conteúdo não encontrado")

            if "<font color=" in content:
                print("🎨 Cores aplicadas ✅")
            else:
                print("❌ Cores não aplicadas")

        else:
            print("❌ Arquivo de log não foi criado!")
            return False

    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_performance():
    """Teste simples de performance"""
    print("\n⚡ Testando performance...")

    start_time = time.time()

    # Cria 50 logs
    for i in range(50):
        log(f"Log de performance {i}", tag="perf")
        if i % 10 == 0:
            info(f"Checkpoint {i}", tag="checkpoint")

    # Força flush
    flush()

    end_time = time.time()
    duration = end_time - start_time

    print(f"⏱️ 50 logs em {duration:.3f} segundos")
    print(f"📊 Performance: {50/duration:.1f} logs/segundo")

    if duration < 1.0:
        print("✅ Performance boa!")
    else:
        print("⚠️ Performance pode melhorar")


if __name__ == "__main__":
    print("🚀 Iniciando testes do HTML Logger...")

    # Teste básico
    if test_basic_functionality():
        # Teste de performance
        test_performance()

        print("\n🎉 Testes concluídos!")
        print("📂 Verifique os arquivos em: test_logs/")
        print("🌐 Abra test_logs/test.html no navegador para testar filtros")
    else:
        print("\n💥 Testes falharam!")
        sys.exit(1)
