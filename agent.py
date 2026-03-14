from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator, current_time
from tools import list_aws_regions, estimate_ec2_cost, get_aws_service_info

load_dotenv()

SYSTEM_PROMPT = """Eres un experto certificado en Amazon Web Services (AWS) con más de 10 años de experiencia.
Respondes siempre en español, de forma clara y precisa.
Cuando expliques conceptos técnicos, usas ejemplos prácticos y mencionas las mejores prácticas de AWS.
Si el usuario pregunta sobre arquitecturas, costos, seguridad o servicios específicos, das recomendaciones concretas.

Tienes acceso a las siguientes herramientas:
- list_aws_regions: lista las regiones de AWS disponibles para un servicio.
- estimate_ec2_cost: estima el costo mensual de una instancia EC2 según su tipo.
- get_aws_service_info: devuelve descripción, casos de uso y documentación de un servicio AWS.
- calculator: realiza cálculos matemáticos.
- current_time: obtiene la fecha y hora actual."""

model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-east-1",
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[list_aws_regions, estimate_ec2_cost, get_aws_service_info, calculator, current_time],
)

def main():
    print("Agente AWS Expert listo. Escribe 'salir' para terminar.\n")
    while True:
        user_input = input("Tú: ").strip()
        if user_input.lower() in ("salir", "exit", "quit"):
            print("Hasta luego.")
            break
        if not user_input:
            continue
        response = agent(user_input)
        print(f"\nAgente: {response}\n")

if __name__ == "__main__":
    main()
