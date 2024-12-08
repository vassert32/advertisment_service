#!/usr/bin/env bash
# Скрипт wait-for-it.sh
# Источник: https://github.com/vishnubob/wait-for-it

set -e

host="$1"
shift
port="$1"
shift
cmd="$@"

until nc -z "$host" "$port"; do
  >&2 echo "Сервер $host:$port не доступен, ожидаем..."
  sleep 1
done

>&2 echo "Сервер $host:$port доступен, запускаем команду."
exec $cmd
