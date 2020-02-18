from __future__ import annotations

import typing as t

import click
import yaml

from ..libs.domains.config import (
    K8sConfig,
    PodConfig,
    WebOptions,
)
from ..libs.domains.logging import GraylogParameters
from .agent.main import main as callisto_main


def read_pod_manifest(ctx: click.Context,
                      param: t.Union[click.Option, click.Parameter],
                      value: str) -> t.Dict[str, t.Any]:
    return yaml.safe_load(value)


@click.command()
@click.option('--web-api-host',
              envvar='WEB_API_HOST',
              default='0.0.0.0',
              help='a host to run web api',
              show_default=True,
              show_envvar=True)
@click.option('--web-api-port',
              envvar='WEB_API_PORT',
              default=8080,
              help='a port to run web api',
              show_default=True,
              show_envvar=True)
@click.option('--log-level',
              envvar='LOG_LEVEL',
              default='INFO',
              help='log level',
              show_default=True,
              show_envvar=True)
@click.option('--graylog-host',
              envvar='GRAYLOG_HOST',
              default=None,
              help='Graylog host address. Logging to Graylog is disabled if left empty',
              show_default=True,
              show_envvar=True)
@click.option('--graylog-port',
              envvar='GRAYLOG_PORT',
              default=12201,
              help='Graylog port',
              show_default=True,
              show_envvar=True)
@click.option('--k8s-in-cluster',
              envvar='K8S_IN_CLUSTER',
              is_flag=True,
              default=True,
              help='Type of run: inside/outside k8s cluster. Needed mostly for debug purposes',
              show_default=True,
              show_envvar=True)
@click.option('--k8s-namespace',
              envvar='K8S_NAMESPACE',
              default='default',
              help='k8s namespace to spawn pods/services',
              show_default=True,
              show_envvar=True)
@click.option('--pod-webdriver-path',
              envvar='POD_WEBDRIVER_PATH',
              default='',
              help='webdriver path location. On selenoid images `/wd/hub` for firefox, empty for others',
              show_default=True,
              show_envvar=True)
@click.option('--pod-webdriver-port',
              envvar='POD_WEBDRIVER_PORT',
              default=4444,
              help='webdriver port',
              show_default=True,
              show_envvar=True)
@click.option('--pod-manifest',
              envvar='POD_MANIFEST',
              type=click.File(),
              callback=read_pod_manifest,
              default='/etc/callisto/pod_manifest.yaml',
              help='Path to pod manifest file',
              show_default=True,
              show_envvar=True)
@click.option('--instance-id',
              envvar='INSTANCE_ID',
              default='unknown',
              help='Unique ID for this callisto instance',
              show_default=True,
              show_envvar=True)
@click.option('--sentry-dsn',
              envvar='SENTRY_DSN',
              default='',
              help='Sentry DSN. Sentry disabled if left empty',
              show_default=True,
              show_envvar=True)
def run_with_options(**options: t.Any) -> None:
    web_parameters = WebOptions(options['web_api_host'], options['web_api_port'])
    log_level = options['log_level']
    k8s_config = K8sConfig(in_cluster=options['k8s_in_cluster'],
                           namespace=options['k8s_namespace'])

    pod_config = PodConfig(
        webdriver_path=options['pod_webdriver_path'],
        webdriver_port=options['pod_webdriver_port'],
        manifest=options['pod_manifest'],
    )

    graylog_config: t.Optional[GraylogParameters] = None
    if options['graylog_host']:
        graylog_config = GraylogParameters(host=options['graylog_host'], port=options['graylog_port'])

    callisto_main(web_parameters=web_parameters,
                  log_level_name=log_level,
                  k8s_config=k8s_config,
                  pod_config=pod_config,
                  instance_id=options['instance_id'],
                  sentry_dsn=options['sentry_dsn'],
                  graylog_config=graylog_config)
