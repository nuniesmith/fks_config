## Multi-stage Dockerfile for fks-config
ARG RUST_VERSION=1.79
FROM rust:${RUST_VERSION} AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo 'fn main(){}' > src/main.rs && cargo build --release || true
RUN rm -rf src
COPY src ./src
RUN cargo build --release --features server

FROM debian:bookworm-slim AS runtime
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /app/target/release/fks-config /usr/local/bin/fks-config
EXPOSE 9000
ENTRYPOINT ["fks-config"]
CMD ["serve", "--port", "9000"]
