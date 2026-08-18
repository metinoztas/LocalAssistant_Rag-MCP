import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """
    Local MCP server'a bağlanır ve tool'ları listeler.
    """

    # MCP server'ın nasıl başlatılacağını tanımla
    server_params = StdioServerParameters(
        command="python",
        args=["mcp/server.py"]
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


            # ---------- "search_files"

            result = await session.call_tool(
                "search_files",
                {"query": "unity"}
            )

            print("\nArama sonuçları:")
            print(result)
            

            # ---------- "get_file_info"

            result = await session.call_tool(
                "get_file_info",
                {
                    "file_path": r"C:\Users\metin\Documents\python.pdf"
                }
            )

            print("\nDosya bilgisi:")
            print(result)


            # ---------- "search_content"

            result = await session.call_tool(
                "search_content",
                {
                    "query": "embedding"
                }
            )

            print("\nİçerik arama sonuçları:")
            print(result)

if __name__ == "__main__":
    asyncio.run(main())