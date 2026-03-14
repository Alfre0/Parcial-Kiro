import boto3
from strands import tool


@tool
def list_aws_regions(service: str = "ec2") -> dict:
    """Lista las regiones de AWS disponibles para un servicio dado."""
    try:
        client = boto3.client("ec2", region_name="us-east-1")
        response = client.describe_regions(AllRegions=False)
        regions = [r["RegionName"] for r in response["Regions"]]
        return {"service": service, "regions": regions, "count": len(regions)}
    except Exception as e:
        return {"error": str(e)}


@tool
def estimate_ec2_cost(instance_type: str, hours: float = 730.0, region: str = "us-east-1") -> dict:
    """Estima el costo mensual aproximado de una instancia EC2 basado en precios on-demand comunes."""
    # Precios on-demand aproximados en USD/hora (us-east-1, Linux)
    pricing = {
        "t3.micro": 0.0104,
        "t3.small": 0.0208,
        "t3.medium": 0.0416,
        "t3.large": 0.0832,
        "t3.xlarge": 0.1664,
        "m5.large": 0.096,
        "m5.xlarge": 0.192,
        "m5.2xlarge": 0.384,
        "c5.large": 0.085,
        "c5.xlarge": 0.17,
        "r5.large": 0.126,
        "r5.xlarge": 0.252,
    }
    price_per_hour = pricing.get(instance_type)
    if not price_per_hour:
        available = list(pricing.keys())
        return {"error": f"Tipo '{instance_type}' no encontrado. Disponibles: {available}"}

    monthly_cost = round(price_per_hour * hours, 2)
    return {
        "instance_type": instance_type,
        "region": region,
        "price_per_hour_usd": price_per_hour,
        "hours": hours,
        "estimated_monthly_cost_usd": monthly_cost,
    }


@tool
def get_aws_service_info(service_name: str) -> dict:
    """Devuelve información general sobre un servicio AWS: descripción, casos de uso y documentación."""
    catalog = {
        "ec2": {
            "full_name": "Amazon Elastic Compute Cloud",
            "description": "Servidores virtuales en la nube con capacidad de cómputo escalable.",
            "use_cases": ["Hosting de aplicaciones", "Procesamiento por lotes", "HPC"],
            "docs": "https://docs.aws.amazon.com/ec2/",
        },
        "s3": {
            "full_name": "Amazon Simple Storage Service",
            "description": "Almacenamiento de objetos con alta durabilidad y disponibilidad.",
            "use_cases": ["Backup", "Data lake", "Hosting de sitios estáticos"],
            "docs": "https://docs.aws.amazon.com/s3/",
        },
        "lambda": {
            "full_name": "AWS Lambda",
            "description": "Ejecución de código sin gestionar servidores (serverless).",
            "use_cases": ["APIs", "Procesamiento de eventos", "Automatización"],
            "docs": "https://docs.aws.amazon.com/lambda/",
        },
        "rds": {
            "full_name": "Amazon Relational Database Service",
            "description": "Bases de datos relacionales gestionadas (MySQL, PostgreSQL, etc.).",
            "use_cases": ["Aplicaciones web", "ERP", "CRM"],
            "docs": "https://docs.aws.amazon.com/rds/",
        },
        "vpc": {
            "full_name": "Amazon Virtual Private Cloud",
            "description": "Red virtual privada aislada dentro de AWS.",
            "use_cases": ["Aislamiento de recursos", "Conectividad híbrida", "Seguridad de red"],
            "docs": "https://docs.aws.amazon.com/vpc/",
        },
        "iam": {
            "full_name": "AWS Identity and Access Management",
            "description": "Gestión de identidades, usuarios, roles y permisos en AWS.",
            "use_cases": ["Control de acceso", "Federación de identidades", "Least privilege"],
            "docs": "https://docs.aws.amazon.com/iam/",
        },
    }
    key = service_name.lower()
    if key in catalog:
        return catalog[key]
    return {
        "error": f"Servicio '{service_name}' no encontrado en el catálogo.",
        "available_services": list(catalog.keys()),
    }


@tool
def comparar_instancias_ec2(instancia_1: str, instancia_2: str) -> dict:
    """Compara dos tipos de instancia EC2 mostrando vCPUs, RAM y precio aproximado por hora."""
    # Especificaciones: (vCPUs, RAM GB, precio on-demand USD/hora us-east-1 Linux)
    specs = {
        "t3.micro":   {"vcpus": 2,  "ram_gb": 1,    "precio_hora": 0.0104},
        "t3.small":   {"vcpus": 2,  "ram_gb": 2,    "precio_hora": 0.0208},
        "t3.medium":  {"vcpus": 2,  "ram_gb": 4,    "precio_hora": 0.0416},
        "t3.large":   {"vcpus": 2,  "ram_gb": 8,    "precio_hora": 0.0832},
        "t3.xlarge":  {"vcpus": 4,  "ram_gb": 16,   "precio_hora": 0.1664},
        "m5.large":   {"vcpus": 2,  "ram_gb": 8,    "precio_hora": 0.096},
        "m5.xlarge":  {"vcpus": 4,  "ram_gb": 16,   "precio_hora": 0.192},
        "m5.2xlarge": {"vcpus": 8,  "ram_gb": 32,   "precio_hora": 0.384},
        "c5.large":   {"vcpus": 2,  "ram_gb": 4,    "precio_hora": 0.085},
        "c5.xlarge":  {"vcpus": 4,  "ram_gb": 8,    "precio_hora": 0.17},
        "r5.large":   {"vcpus": 2,  "ram_gb": 16,   "precio_hora": 0.126},
        "r5.xlarge":  {"vcpus": 4,  "ram_gb": 32,   "precio_hora": 0.252},
    }

    errores = []
    for inst in [instancia_1, instancia_2]:
        if inst not in specs:
            errores.append(inst)

    if errores:
        return {
            "error": f"Instancia(s) no encontrada(s): {errores}",
            "instancias_disponibles": list(specs.keys()),
        }

    s1 = specs[instancia_1]
    s2 = specs[instancia_2]

    def diferencia(val1, val2):
        if val1 == val2:
            return "igual"
        pct = round(abs(val1 - val2) / min(val1, val2) * 100, 1)
        mayor = instancia_1 if val1 > val2 else instancia_2
        return f"{mayor} es {pct}% mayor"

    return {
        "comparacion": {
            instancia_1: s1,
            instancia_2: s2,
        },
        "diferencias": {
            "vcpus": diferencia(s1["vcpus"], s2["vcpus"]),
            "ram_gb": diferencia(s1["ram_gb"], s2["ram_gb"]),
            "precio_hora": diferencia(s1["precio_hora"], s2["precio_hora"]),
        },
        "recomendacion": (
            f"{instancia_1} es más económica"
            if s1["precio_hora"] < s2["precio_hora"]
            else f"{instancia_2} es más económica"
        ),
        "region": "us-east-1",
        "nota": "Precios on-demand aproximados para Linux.",
    }
