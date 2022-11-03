{{- define "partials.noop" -}}
securityContext:
  runAsUser: 65535
args:
- -v
image: "{{.Values.image.registry}}/{{.Values.noop.image.name}}:{{.Values.noop.image.version}}"
name: noop
{{- end -}}
