"""Console entry point using click"""
import json
import sys
import click
from .passwords import generate_password, analyze_password
from .iocs import extract_iocs
from .logs import anonymize_text
from .pcap import pcap_summary

@click.group()
def main():
    """safetybox — defensive security utilities"""
    pass

@main.command('gen-pass')
@click.option('--length', '-l', default=16, type=int)
@click.option('--charset', default='all', type=click.Choice(['all','alnum','hex']))
@click.option('--pronounceable', is_flag=True)
def gen_pass(length, charset, pronounceable):
    click.echo(generate_password(length=length, charset=charset, pronounceable=pronounceable))

@main.command('check-pass')
@click.argument('password')
def check_pass(password):
    analysis = analyze_password(password)
    click.echo(json.dumps(analysis.__dict__, ensure_ascii=False, indent=2))

@main.command('extract-iocs')
@click.option('--file', '-f', type=click.Path(exists=True), default=None)
def extract_iocs_cmd(file):
    if file:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    click.echo(json.dumps(extract_iocs(text), ensure_ascii=False, indent=2))

@main.command('anonymize-logs')
@click.option('--file', '-f', type=click.Path(exists=True), default=None)
@click.option('--keep-last-octet', is_flag=True)
def anonymize_logs(file, keep_last_octet):
    if file:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                click.echo(anonymize_text(line.rstrip('\n'), keep_last_octet=keep_last_octet))
    else:
        for line in sys.stdin:
            click.echo(anonymize_text(line.rstrip('\n'), keep_last_octet=keep_last_octet))

@main.command('pcap-summary')
@click.argument('path', type=click.Path(exists=True))
@click.option('--max-packets', type=int, default=0)
def cmd_pcap_summary(path, max_packets):
    click.echo(json.dumps(pcap_summary(path, max_packets=max_packets), ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
