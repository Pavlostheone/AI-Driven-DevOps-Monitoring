FROM alpine

RUN apka add --no-cache bash curl kubectl

COPY scripts/ /scripts/
CMD ["/scripts/collect_kubernetes.sh"]