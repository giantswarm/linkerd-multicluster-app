{{- define "partials.noop" -}}
securityContext:
  runAsUser: 65535
args:
- -v
image: "{{.Values.image.registry}}/{{.Values.noop.image.name}}:{{.Values.noop.image.version}}"
name: noop
resources:
  limits:
    cpu: "50m"
    memory: "10Mi"
  requests:
    cpu: "50m"
    memory: "10Mi"
securityContext:
  runAsUser: {{ .Values.proxyInit.runAsUser | int | eq 0 | ternary 65534 .Values.proxyInit.runAsUser }}
{{- end -}}
