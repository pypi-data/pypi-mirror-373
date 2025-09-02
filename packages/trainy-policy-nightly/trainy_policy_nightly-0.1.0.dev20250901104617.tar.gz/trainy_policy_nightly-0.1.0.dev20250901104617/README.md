# Trainy Skypilot Policy

This is a package that defines the Skypilot policies necessary for running on Trainy clusters. The purpose of the policy is to 

- mutate tasks to add the necessary labels/annotations (kueue, networking, etc.) per cloud provider
- set the available k8s clusters to be those that are visible via tailscale in the allowed k8s cluster contexts

For users, they set in `~/.sky/config.yaml`

```bash
admin_policy: trainy.policy.DynamicKubernetesContextsUpdatePolicy
```

and install
```bash
pip install "trainy-skypilot-nightly[kubernetes]"
pip install trainy-policy-nightly
```

[Skypilot Admin Policies](https://skypilot.readthedocs.io/en/latest/cloud-setup/policy.html)