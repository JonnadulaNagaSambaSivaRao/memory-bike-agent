# main.py

import asyncio
from agent import run_agent, show_memories, clear_memories


# ============================================================
# MAIN CLI APPLICATION
# ============================================================

async def main():

    print("\n" + "=" * 60)
    print("        🧠 MEMORY-AWARE AI AGENT")
    print("=" * 60)

    print("\nAgent started successfully!")
    print("Type your message and press Enter.")
    print("\nAvailable commands:")
    print("  show memory   → Display saved long-term memories")
    print("  clear memory  → Delete all long-term memories")
    print("  exit          → Exit the application")

    print("=" * 60)

    while True:

        try:

            # ------------------------------------------------
            # Get user input
            # ------------------------------------------------

            user_input = input("\nYou: ").strip()

            # ------------------------------------------------
            # Ignore empty input
            # ------------------------------------------------

            if not user_input:
                continue

            # ------------------------------------------------
            # Exit
            # ------------------------------------------------

            if user_input.lower() in {
                "exit",
                "quit",
                "bye"
            }:

                print("\nAgent: Goodbye! 👋")
                break

            # ------------------------------------------------
            # Show memory
            # ------------------------------------------------

            if user_input.lower() == "show memory":

                show_memories()
                continue

            # ------------------------------------------------
            # Clear memory
            # ------------------------------------------------

            if user_input.lower() == "clear memory":

                confirmation = input(
                    "\nAre you sure you want to clear "
                    "all long-term memory? (yes/no): "
                ).strip().lower()

                if confirmation == "yes":

                    clear_memories()

                else:

                    print(
                        "Memory was not cleared."
                    )

                continue

            # ------------------------------------------------
            # Run Memory-Aware AI Agent
            # ------------------------------------------------

            print("\nAgent: Thinking...")

            response = await run_agent(
                user_input
            )

            # ------------------------------------------------
            # Display response
            # ------------------------------------------------

            print(
                f"\nAgent: {response}"
            )

        except KeyboardInterrupt:

            print(
                "\n\nAgent: Goodbye! 👋"
            )

            break

        except Exception as e:

            print(
                f"\nError: {e}"
            )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())