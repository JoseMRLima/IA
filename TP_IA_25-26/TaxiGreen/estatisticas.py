import matplotlib.pyplot as plt
import json

STATSFILENAME = "data/estatisticas.json"

def mostrar_estatisticas():
    with open(STATSFILENAME, "r") as file:
        content = json.load(file)

    categories = []
    values = [[],[],[],[],[],[],[],[]]
    for obj in content:
        categories.append(obj["algoritmo"])
        values[0].append(obj["temp_med_resp"])
        values[1].append(obj["taxa_ocupacao"])
        values[2].append(obj["custo_operacional"])
        values[3].append(obj["emissao_CO2"])
        values[4].append(obj["nr_ped_rej"])
        values[5].append(obj["km_s_pass"])
        values[6].append(obj["carros_bloq"])
        values[7].append(obj["perc_media_lugares"])

    ylabels = [
        "Tempo Médio Resposta (seg)",
        "Taxa de Ocupação Média",
        "Custo Operacional",
        "Emissões CO2",
        "Nr Pedidos Rejeitados",
        "Metros sem Passageiros",
        "Nr Carros Bloqueados",
        "Media Lugares Vazios (%)"
    ]

    fig, axes = plt.subplots(
        2, 4,
        figsize=(25, 12)
    )

    axes = axes.flatten()

    for ax, y, ylabel in zip(axes, values, ylabels):
        ax.bar(categories, y)
        ax.set_ylabel(ylabel)

    plt.tight_layout()
    plt.show()

