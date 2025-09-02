#!/usr/bin/env python3
import requests
import argparse

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('num', type=int)
	args = ap.parse_args()

	endpoint = 'https://pypi.org/pypi/PySide6/json'
	all_releases = list(requests.get(endpoint).json()['releases'].keys())
	for i, ver in enumerate(all_releases[0-args.num:]):
		print(f'rel{args.num-i-1}={ver}')


if __name__ == '__main__':
	main()
