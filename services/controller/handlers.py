import logging
import os.path
import kopf
import kubernetes.client
import yaml


MANIFESTS_DIR = "manifests"


def parse_manifest(filename, **values):
    path = os.path.join(os.path.dirname(__file__), MANIFESTS_DIR, filename)
    tmpl = open(path, "rt").read()
    text = tmpl.format(**values)
    return yaml.safe_load(text)


@kopf.on.create("inferencebackends")
def create_fn(spec, name, namespace, logger, **kwargs):
    redis_deployment_manifest = parse_manifest("redis-deployment.yaml",
                                               name=name)
    redis_service_manifest = parse_manifest("redis-service.yaml",
                                            name=name)
    deployment_manifest = parse_manifest("deployment.yaml",
                                         model_id=spec.get("modelId"),
                                         name=name,
                                         namespace=namespace)
    service_manifest = parse_manifest("service.yaml",
                                      name=name)

    kopf.adopt([
        redis_deployment_manifest,
        redis_service_manifest,
        deployment_manifest,
        service_manifest
    ])

    apps_api = kubernetes.client.AppsV1Api()
    core_api = kubernetes.client.CoreV1Api()

    redis_deployment_obj = apps_api.create_namespaced_deployment(
        namespace=namespace,
        body=redis_deployment_manifest
    )
    logger.info(f"Redis deployment created.")

    redis_service_obj = core_api.create_namespaced_service(
        namespace=namespace,
        body=redis_service_manifest
    )
    logger.info(f"Redis service created.")

    deployment_obj = apps_api.create_namespaced_deployment(
        namespace=namespace,
        body=deployment_manifest
    )
    logger.info(f"Deployment created.")

    service_obj = core_api.create_namespaced_service(
        namespace=namespace,
        body=service_manifest
    )
    logger.info(f"Service created.")

    return {
        "redis-deployment-name": redis_deployment_obj.metadata.name,
        "redis-service-name": redis_service_obj.metadata.name,
        "deployment-name": deployment_obj.metadata.name,
        "service-name": service_obj.metadata.name
    }


@kopf.on.update("inferencebackends")
def update_fn(spec, status, namespace, logger, **kwargs):
    secret_name = status["create_fn"]["secret-name"]
    secret_patch = {
        "stringData": {
            "MODEL_ID": spec.get("modelId")
        }
    }

    core_api = kubernetes.client.CoreV1Api()
    core_api.patch_namespaced_secret(
        namespace=namespace,
        name=secret_name,
        body=secret_patch,
    )

    logger.info(f"Secret {secret_name} patched with model id {spec.get('modelId')}")


@kopf.on.field("inferencebackends", field="metadata.labels")
def relabel(diff, status, namespace, **kwargs):
    # TODO: Fix diff logic when label field didn't exist
    raise kopf.PermanentError("Relabeling logic not implemented!")

    deployment_name = status["create_fn"]["deployment-name"]
    service_name = status["create_fn"]["service-name"]
    secret_name = status["create_fn"]["secret-name"]
    logging.info(f"=> diff: {diff}")
    labels_patch = {
        field[0]: new for op, field, old, new in diff
    }

    patch = {
        "metadata": {
            "labels": labels_patch
        }
    }

    apps_api = kubernetes.client.AppsV1Api()
    core_api = kubernetes.client.CoreV1Api()

    apps_api.patch_namespaced_deployment(
        namespace=namespace,
        name=deployment_name,
        body=patch
    )

    core_api.patch_namespaced_service(
        namespace=namespace,
        name=service_name,
        body=patch
    )

    core_api.patch_namespaced_secret(
        namespace=namespace,
        name=secret_name,
        body=patch
    )
