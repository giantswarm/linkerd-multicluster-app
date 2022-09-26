{{- define "partials.noop" -}}
securityContext:
  runAsUser: 65535
args:
- -v
image: gcr.io/google_containers/pause:3.2
name: noop
{{- end -}}
