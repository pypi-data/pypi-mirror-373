import sys
import json

import jinja2
import requests

mock_dict = {
    "delete": """""",
    "get": """{"item": "get"}""",
    "head": """""",
    "list": """{"items": [{"item": "a"},{"item": "b"}]}""",
    "patch": """""",
    "post": """""",
    "put": """""",
}

fabric_template = """
{% block head -%}
apiVersion: zalando.org/v1
kind: FabricGateway
metadata:
  labels:
    application: {{application}}
  {%- if component %}
    component: {{component}}
  {%- endif %}
  {%- if team %}
    team: {{team}}
  {%- endif %}
  name: {{app}}
  namespace: {{application}}
spec:
  paths:
{%- endblock -%}

{%- for p in paths %}
    {{base+p}}:
    {%- for m in paths[p] %}
      {{m}}:
      {%- if paths[p][m] is defined and paths[p][m]|length >0 %}
        x-fabric-privileges:
       {%- for scope in paths[p][m] %}
        - {{scope}}
       {%- endfor -%}
      {%- elif defaultScopes %}
        x-fabric-privileges:
       {%- for scope in defaultScopes %}
        - {{scope}}
       {%- endfor -%}
      {%- elif mock and mock[m] %}
        x-fabric-custom-routes:
          - x-fabric-match:
              headers:
                X-Frontend-Type: browser
            x-fabric-privileges:
              - "uid"
            x-fabric-static-response:
              status: 200
              headers:
                Content-Type: application/json
              body: |
                {{ mock[m] }}
          - x-fabric-match:
              headers:
                X-Frontend-Type: mobile-app
            x-fabric-privileges:
              - "uid"
            x-fabric-static-response:
              status: 200
              headers:
                Content-Type: application/json
              body: |
                {{ mock[m] }}
      {%- else %}
        {}
      {%- endif %}
    {%- endfor -%}
{% endfor -%}

{%- block trailer %}
  x-fabric-service:
  - host: {{host}}
    serviceName: {{app}}
    servicePort: main

{%- if members %}
  x-fabric-admins:
{%- for member in members %}
  - {{member}}
{%- endfor -%}
{%- endif -%}

{% endblock %}
---
apiVersion: v1
kind: Service
metadata:
  annotations:
  labels:
    application: {{application}}
  {%- if component %}
    component: {{component}}
  {%- endif %}
  name: {{app}}
  namespace: {{application}}
spec:
  ports:
  - name: main
    port: {{backendport}}
    targetPort: {{backendport}}
  selector:
{%- if component %}
    component: {{component}}
{%- endif %}
    application: {{application}}
  type: ClusterIP
"""


def fabric(token, application, component, team, backendport, file, mock, debug):
    if not component:
        app = application
    else:
        app = application + "-" + component

    if not backendport or backendport == 0:
        backendport = 8080

    members = []
    if team:
        teamURL = "https://teams.auth.zalando.com/api/teams/{}".format(team)
        rsp = requests.get(teamURL, timeout=10, headers={"Authorization": "Bearer {}".format(token)})
        rsp.raise_for_status()
        body = rsp.json()
        members = body["member"]
    if debug:
        print("*** team members: {}".format(members))

    if file:
        f = open(file, "r")
        api = json.load(f)
        f.close()
    else:
        revisionsURL = (
            "https://infrastructure-api-repository.zalandoapis.com/api-revisions?states=ACTIVE&applications={}".format(
                application
            )
        )
        response = requests.get(revisionsURL, timeout=10, headers={"Authorization": "Bearer {}".format(token)})
        response.raise_for_status()

        revisions = response.json()
        if len(revisions["api_revisions"]) == 0:
            print("ERR: no revisions found for application: {}".format(application))
            exit(1)

        # take first as a guess because we can only use one, maybe request input from the use to choose the right one
        revision = revisions["api_revisions"][0]
        apiURL = revision["href"]
        if debug:
            print("*** apiURL: {}".format(apiURL))

        rsp = requests.get(
            apiURL,
            timeout=10,
            headers={
                "Authorization": "Bearer {}".format(token),
                "Accept": "application/json",
            },
        )
        rsp.raise_for_status()
        api = rsp.json()

    host = api.get("host", "unknown.host")
    base_path = api.get("basePath", "/")
    if base_path[-1] == "/":
        base_path = base_path[:-1]

    defaultScopes = []
    securityKeys = []
    if "components" in api:
        apiComp = api["components"]
        if "securitySchemes" in apiComp:
            secSchemes = apiComp["securitySchemes"]
            if debug:
                print("*** secSchemes: {}".format(secSchemes))
            # this should be the keys to check in api['security'], but nobody does it
            # securityKeys=secSchemes.keys()
            # print("securityKeys: {}".format(securityKeys))
            # try to guess what people do
            if "OAuth2" in secSchemes:
                scopeMap = secSchemes["OAuth2"].get("flows", {}).get("clientCredentials", {}).get("scopes", {})
                defaultScopes = list(scopeMap.keys())
            if "oauth2" in secSchemes:
                scopeMap = secSchemes["oauth2"].get("flows", {}).get("clientCredentials", {}).get("scopes", {})
                defaultScopes = list(scopeMap.keys())
    defaultScopes = list(set(defaultScopes))
    if debug:
        print("*** defaultScopes: {}".format(defaultScopes))

    if debug and "security" in api:
        secObjList = api["security"]
        if len(secObjList) > 0:
            print("*** secObjList>0: {}".format(secObjList))
            for secObj in secObjList:
                if "BearerAuth" in secObj:
                    print("-> BearerAuth: {}".format(secObj["BearerAuth"]))
                elif "bearerauth" in secObj:
                    print("-> bearerauth: {}".format(secObj["bearerauth"]))
                elif "oauth2" in secObj:
                    print("-> oauth2: {}".format(secObj["oauth2"]))
                elif "OAuth2" in secObj:
                    print("-> OAuth2: {}".format(secObj["OAuth2"]))

    paths = api["paths"]
    templatePaths = {}

    for p in paths:
        templatePaths[p] = templatePaths.get(p, {})
        methods = paths[p]
        for m in methods:
            # clean data
            if not m.lower() in ["get", "head", "post", "put", "patch", "delete", "options", "trace", "connect"]:
                continue

            templatePaths[p][m] = templatePaths[p].get(m, [])
            o = methods[m]
            if "security" in o:
                if debug:
                    print("*** o['security']: {}".format(o["security"]))
                secObjs = o["security"]
                scopes = set()
                for secObj in secObjs:
                    bearerScopes = secObj.get("bearer", [])
                    oauthScopes = secObj.get("oauth2", [])
                    scopes = scopes.union(set(bearerScopes + oauthScopes))
                    try:
                        for v in secObj.values():
                            scopes = scopes.union(v)
                    except:
                        pass

                if debug:
                    print("*** ", p, m.upper(), list(scopes))
                templatePaths[p][m] = list(scopes)

    if mock:
        mock = mock_dict
    template = jinja2.Template(fabric_template)
    print(
        template.render(
            app=app,
            application=application,
            component=component,
            team=team,
            host=host,
            backendport=backendport,
            paths=templatePaths,
            base=base_path,
            members=members,
            defaultScopes=defaultScopes,
            mock=mock,
        ).strip()
    )
    print(
        "For more information please check our docs https://fabric.docs.zalando.net/fabric-gateway-features/",
        file=sys.stderr,
    )


ingress_template = """
{% block head -%}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
{%- if ui %}
    zalando.org/skipper-filter: grantFlow()
{%- else %}
  {%- if scopes %}
    zalando.org/skipper-filter: oauthTokeninfoAllScope("{{scopes}}")
  {%- else %}
    zalando.org/skipper-filter: oauthTokeninfoAllScope("uid")
  {%- endif %}
{%- endif %}
  labels:
    application: {{application}}
  {%- if component %}
    component: {{component}}
  {%- endif %}
  {%- if team %}
    team: {{team}}
  {%- endif %}
  name: {{app}}
  namespace: {{application}}
spec:
  rules:
{%- endblock -%}

{%- for host in hosts %}
  - host: {{host}}
    http:
      paths:
      - backend:
          service:
            name: {{app}}
            port:
              name: main
        pathType: ImplementationSpecific
{%- endfor %}
---
apiVersion: v1
kind: Service
metadata:
  annotations:
  labels:
    application: {{application}}
  {%- if component %}
    component: {{component}}
  {%- endif %}
  name: {{app}}
  namespace: {{application}}
spec:
  ports:
  - name: main
    port: {{backendport}}
    targetPort: {{backendport}}
  selector:
{%- if component %}
    component: {{component}}
{%- endif %}
    application: {{application}}
  type: ClusterIP
"""


def ingress(application, component, team, host, backendport, scopes, ui, debug):
    if not component:
        app = application
    else:
        app = application + "-" + component

    hosts = host.split(",")

    if not backendport or backendport == 0:
        backendport = 8080

    if scopes:
        scopes = '","'.join(scopes.split(","))

    template = jinja2.Template(ingress_template)
    print(
        template.render(
            app=app,
            application=application,
            component=component,
            team=team,
            hosts=hosts,
            backendport=backendport,
            scopes=scopes,
            ui=ui,
        ).strip()
    )
    if ui:
        print(
            "For more information about enduser authentication please check our docs https://sunrise.zalando.net/docs/default/Documentation/cloud/howtos/authenticate-endusers/index.html",
            file=sys.stderr,
        )
    if not scopes:
        print(
            "For more information about scopes, please check our docs https://sunrise.zalando.net/docs/default/Documentation/cloud/howtos/oauth2-tokens/index.html",
            file=sys.stderr,
        )


deployment_template = """
{%- if autoscaling %}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  labels:
    application: {{application}}
{%- if component %}
    component: {{component}}
{%- endif %}
{%- if team %}
    team: {{team}}
{%- endif %}
  name: {{app}}
  namespace: {{application}}
spec:
  maxReplicas: 10
  metrics:
  - resource:
      name: cpu
      target:
        averageUtilization: 60
        type: Utilization
    type: Resource
  minReplicas: 3
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{app}}
---
{%- endif %}
{%- if secret %}
apiVersion: v1
data:
  api-key: "use: zkubectl encrypt to KMS encrypt secret for the logged in cluster"
kind: Secret
metadata:
  labels:
    application: {{application}}
{%- if component %}
    component: {{component}}
{%- endif %}
{%- if team %}
    team: {{team}}
{%- endif %}
  name: {{app}}
  namespace: {{application}}
type: Opaque
---
{%- endif %}

{%- if scopes %}
apiVersion: zalando.org/v1
kind: PlatformCredentialsSet
metadata:
  labels:
    application: {{application}}
{%- if component %}
    component: {{component}}
{%- endif %}
{%- if team %}
    team: {{team}}
{%- endif %}
  name: {{app}}
  namespace: {{application}}
spec:
  application: {{application}}
  tokens:
    {{application}}:
      privileges:
{%- for scope in scopes %}
      - {{scope}}
{%- endfor %}
---
{%- endif %}

{%- if config %}
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    application: {{application}}
{%- if component %}
    component: {{component}}
{%- endif %}
{%- if team %}
    team: {{team}}
{%- endif %}
  name: {{app}}
  namespace: {{application}}
data:
  # in your container /config/config.yaml
  config.yaml: |-
    foo: bar
    baz: qux
---
{%- endif %}
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    application: {{application}}
{%- if component %}
    component: {{component}}
{%- endif %}
{%- if team %}
    team: {{team}}
{%- endif %}
  name: {{app}}
  namespace: {{application}}
spec:
{%- if not autoscaling %}
  replicas: 3
{%- endif %}
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      deployment: {{app}}
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      labels:
        application: {{application}}
{%- if component %}
        component: {{component}}
{%- endif %}
{%- if team %}
        team: {{team}}
{%- endif %}
        deployment: {{app}}
    spec:
      containers:
      - args:
        - /{{app}}
        - -address=:{{backendport}}
{%- if config %}
        - -config=/config/config.yaml
{%- endif %}
{%- if secret %}
        env:
        - name: KEY
          valueFrom:
            secretKeyRef:
              key: api-key
              name: {{app}}
{%- endif %}
        image: {{image}}
        name: {{app}}
        ports:
        - containerPort: {{backendport}}
          name: main
          protocol: TCP
        readinessProbe:
          failureThreshold: 1
          httpGet:
            path: /health
            port: {{backendport}}
            scheme: HTTP
          initialDelaySeconds: 1
          periodSeconds: 10
          successThreshold: 1
          timeoutSeconds: 3
        resources:
          limits:
            cpu: "{{cpu}}"
            memory: {{memory}}
          requests:
            cpu: "{{cpu}}"
            memory: {{memory}}
        securityContext:
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 5000
{%- if config or scopes %}
        volumeMounts:
 {%- if config %}
        - mountPath: /config
          name: config
          readOnly: true
 {%- endif %}
 {%- if scopes %}
        - mountPath: /meta/token-credentials
          name: token-credentials
          readOnly: true
 {%- endif %}
      volumes:
 {%- if config %}
      - configMap:
          defaultMode: 420
          name: {{app}}
        name: config
 {%- endif %}
 {%- if scopes %}
      - name: token-credentials
        secret:
          defaultMode: 420
          secretName: {{app}}-token-credentials
 {%- endif %}
{%- endif %}
"""


def deployment(
    application, component, team, backendport, scopes, image, cpu, memory, cluster, config, secret, autoscaling, debug
):
    if not component:
        app = application
    else:
        app = application + "-" + component

    if not backendport:
        backendport = 8080

    if not image:
        image = "container-registry-test.zalando.net/{}/{}:v0.0.1".format(team or "MYTEAM", app)

    if not cpu:
        cpu = "100m"

    if not memory:
        memory = "1Gi"

    if scopes:
        scopes = scopes.split(",")

    template = jinja2.Template(deployment_template)
    print(
        template.render(
            app=app,
            application=application,
            component=component,
            team=team,
            backendport=backendport,
            scopes=scopes,
            image=image,
            cpu=cpu,
            memory=memory,
            cluster=cluster,
            config=config,
            secret=secret,
            autoscaling=autoscaling,
        ).strip()
    )


stackset_template = """
{%- if secret %}
apiVersion: v1
data:
  api-key: "use: zkubectl encrypt to KMS encrypt secret for the logged in cluster"
kind: Secret
metadata:
  labels:
    application: {{application}}
{%- if component %}
    component: {{component}}
{%- endif %}
{%- if team %}
    team: {{team}}
{%- endif %}
  name: {{app}}
  namespace: {{application}}
type: Opaque
---
{%- endif %}

{%- if scopes %}
apiVersion: zalando.org/v1
kind: PlatformCredentialsSet
metadata:
  labels:
    application: {{application}}
{%- if component %}
    component: {{component}}
{%- endif %}
{%- if team %}
    team: {{team}}
{%- endif %}
  name: {{app}}
  namespace: {{application}}
spec:
  application: {{application}}
  tokens:
    {{application}}:
      privileges:
{%- for scope in scopes %}
      - {{scope}}
{%- endfor %}
---
{%- endif %}

{%- if config %}
apiVersion: v1
kind: ConfigMap
metadata:
  labels:
    application: {{application}}
{%- if component %}
    component: {{component}}
{%- endif %}
{%- if team %}
    team: {{team}}
{%- endif %}
  name: {{app}}
  namespace: {{application}}
data:
  # in your container /config/config.yaml
  config.yaml: |-
    foo: bar
    baz: qux
---
{%- endif %}
apiVersion: zalando.org/v1
kind: StackSet
metadata:
  labels:
    application: {{application}}
{%- if component %}
    component: {{component}}
{%- endif %}
{%- if team %}
    team: {{team}}
{%- endif %}
  name: {{app}}
  namespace: {{application}}
spec:
  ingress:
    backendPort: {{backendport}}
{%- for host in hosts %}
    hosts:
    - {{host}}
{%- endfor %}
    metadata:
      annotations:
        zalando.org/skipper-filter: oauthTokeninfoAllScopes("uid")
      labels:
        application: {{application}}
      {%- if component %}
        component: {{component}}
      {%- endif %}
      {%- if team %}
        team: {{team}}
      {%- endif %}
  stackLifecycle:
    limit: 3
    scaledownTTLSeconds: 1800
  stackTemplate:
    metadata: {}
      labels:
        application: {{application}}
{%- if component %}
        component: {{component}}
{%- endif %}
{%- if team %}
        team: {{team}}
{%- endif %}
        deployment: {{app}}
    spec:
{%- if autoscaling %}
      autoscaler:
        maxReplicas: 10
        metrics:
        - averageUtilization: 60
          type: CPU
        minReplicas: 3
{%- else %}
      replicas: 3
{%- endif %}
      podTemplate:
        metadata:
          labels:
            application: {{application}}
{%- if component %}
            component: {{component}}
{%- endif %}
{%- if team %}
            team: {{team}}
{%- endif %}
            deployment: {{app}}
        spec:
          containers:
          - args:
            - /{{app}}
            - -address=:{{backendport}}
{%- if config %}
            - -config=/config/config.yaml
{%- endif %}
{%- if secret %}
            env:
            - name: KEY
              valueFrom:
                secretKeyRef:
                  key: api-key
                  name: {{app}}
{%- endif %}
            image: {{image}}
            name: {{app}}
            ports:
            - containerPort: {{backendport}}
              name: main
              protocol: TCP
            readinessProbe:
              failureThreshold: 1
              httpGet:
                path: /health
                port: {{backendport}}
                scheme: HTTP
              initialDelaySeconds: 1
              periodSeconds: 10
              successThreshold: 1
              timeoutSeconds: 3
            resources:
              limits:
                cpu: "{{cpu}}"
                memory: {{memory}}
              requests:
                cpu: "{{cpu}}"
                memory: {{memory}}
            securityContext:
              readOnlyRootFilesystem: true
              runAsNonRoot: true
              runAsUser: 5000
{%- if config or scopes %}
            volumeMounts:
  {%- if config %}
            - mountPath: /config
              name: config
              readOnly: true
  {%- endif %}
  {%- if scopes %}
            - mountPath: /meta/token-credentials
              name: token-credentials
              readOnly: true
  {%- endif %}
          volumes:
  {%- if config %}
          - configMap:
              defaultMode: 420
              name: {{app}}
            name: config
  {%- endif %}
  {%- if scopes %}
          - name: token-credentials
            secret:
              defaultMode: 420
              secretName: {{app}}-token-credentials
  {%- endif %}
{%- endif %}
"""


def stackset(
    application,
    component,
    team,
    host,
    backendport,
    scopes,
    image,
    cpu,
    memory,
    cluster,
    config,
    secret,
    ui,
    autoscaling,
    debug,
):
    if not component:
        app = application
    else:
        app = application + "-" + component

    hosts = host.split(",")

    if not backendport:
        backendport = 8080

    if not image:
        image = "container-registry-test.zalando.net/{}/{}:v0.0.1".format(team or "MYTEAM", app)

    if not cpu:
        cpu = "100m"

    if not memory:
        memory = "1Gi"

    if scopes:
        scopes = scopes.split(",")

    template = jinja2.Template(stackset_template)
    print(
        template.render(
            app=app,
            application=application,
            component=component,
            team=team,
            hosts=hosts,
            backendport=backendport,
            scopes=scopes,
            image=image,
            cpu=cpu,
            memory=memory,
            cluster=cluster,
            config=config,
            secret=secret,
            ui=ui,
            autoscaling=autoscaling,
        ).strip()
    )
