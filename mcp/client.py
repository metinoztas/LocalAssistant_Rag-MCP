import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import sys



async def main():
    """
    Local MCP server'a bağlanır ve tool'ları listeler.
    """

    # MCP server'ın nasıl başlatılacağını tanımla
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"]
    )

    # Server'a stdio üzerinden bağlan
    async with stdio_client(server_params) as (read, write): 
    # bu kod sayesinde server.py'yi çalıştırmaya gerek yok stdio_client() MCP server'ı başlatıyor

        # MCP oturumu oluştur
        async with ClientSession(read, write) as session:

            # MCP bağlantısını başlat
            await session.initialize()

            print("MCP server bağlantısı başarılı.")

            # Server'daki tool'ları listele
            tools = await session.list_tools()

            print("\nKullanılabilir tool'lar:")

            for tool in tools.tools:
                print(f"- {tool.name}")




            print("*"*20)
            # ---------- "search_files"

            result = await session.call_tool(
                "search_files",
                {"query": "python"}
            )

            print("\nArama sonuçları:")
            print(result)



            
            print("*"*20)
            # ---------- "get_file_info"

            result = await session.call_tool(
                "get_file_info",
                {
                    "file_path": r"C:\Users\metin\Documents\python.pdf"
                }
            )

            print("\nDosya bilgisi:")
            print(result)



            print("*"*20)
            # ---------- "search_content"

            result = await session.call_tool(
                "search_content",
                {
                    "query": "embedding"
                }
            )

            print("\nİçerik arama sonuçları:")

            results = result.structured_content.get("result", [])

            for item in results:
                print(f"- {item['name']}")
                print(f"  {item['path']}")




            print("*"*20)
            #---------------- list_directory

            result = await session.call_tool(
                "list_directory",
                {
                    "directory_path": r"C:\Users\metin\Documents"
                }
            )

            print("\nKlasör içeriği:")
            print(result)


            print("*"*20)
            # ----------------- get_recent_files

            result = await session.call_tool(
                "get_recent_files",
                {
                    "limit": 5
                }
            )

            print("\nSon değiştirilen dosyalar:")
            print(result)


            print("*"*20)
            # ------------------ get_rag_index_status

            result = await session.call_tool(
                "get_rag_index_status",
                {
                    "file_path": r"C:\Users\metin\Documents\28102826_Python-Ders-Notlari-1.pdf"
                }
            )

            print("\nRAG indeks durumu:")
            print(result)




if __name__ == "__main__":
    asyncio.run(main())