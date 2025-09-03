import pytest
from rich.color_triplet import ColorTriplet
from rich.console import Console

from bear_dereth.tools.graphics.bear_gradient import ColorGradient


@pytest.mark.visual
def test_gradients_visual():
    console = Console()

    # Health meter goes from red (low health) to green (full health)
    health_gradient = ColorGradient()

    console.print("🏥 [bold]Health Meter Demonstration[/bold] 🏥\n")

    # Normal health: Red (low) -> Green (high)
    console.print("[bold green]Normal Health Levels (0% = Critical, 100% = Perfect):[/bold green]")
    for health in range(0, 101, 10):
        color: ColorTriplet = health_gradient.map_to_color(0, 100, health)
        health_bar = "█" * (health // 5)
        console.print(f"HP: {health:3d}/100 {health_bar:<20}", style=color.rgb)

    health_scenarios = [
        (5, "💀 Nearly Dead"),
        (25, "🩸 Critical Condition"),
        (50, "⚠️  Wounded"),
        (75, "😐 Recovering"),
        (95, "💪 Almost Full Health"),
        (100, "✨ Perfect Health"),
    ]

    console.print("[bold green]Health Status Examples:[/bold green]")
    for hp, status in health_scenarios:
        color: ColorTriplet = health_gradient.map_to_color(0, 100, hp)
        console.print(f"{status}: {hp}/100 HP", style=color.rgb)

    console.print("\n" + "=" * 50 + "\n")

    # Reversed: Infection/Damage meter (Green = good, Red = bad)
    console.print("[bold red]Infection Level (0% = Healthy, 100% = Critical):[/bold red]")
    health_gradient.reverse = True
    for infection in range(0, 101, 10):
        color: ColorTriplet = health_gradient.map_to_color(0, 100, infection)
        infection_bar = "█" * (infection // 5)
        status = "🦠" if infection > 70 else "⚠️" if infection > 30 else "✅"
        console.print(f"Infection: {infection:3d}% {infection_bar:<20} {status}", style=color.rgb)

    infected_scenarios = [
        (5, "✅ Healthy"),
        (25, "⚠️ Mild Infection"),
        (50, "🦠 Moderate Infection"),
        (75, "🦠 Severe Infection"),
        (100, "💀 Critical Condition"),
    ]

    console.print("[bold red]Infection Status Examples:[/bold red]")
    for ip, status in infected_scenarios:
        color: ColorTriplet = health_gradient.map_to_color(0, 100, ip)
        console.print(f"{status}: {ip}/100 Infection", style=color.rgb)
