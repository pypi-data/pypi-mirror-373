

build:
	docker build -t img2text .


run:
	docker run -it --rm img2text $(IMAGE)


run-piped:
	docker run -i --rm img2text


run-clip:
	docker run -it --rm \
  -e XDG_RUNTIME_DIR=$$XDG_RUNTIME_DIR \
  -v $XDG_RUNTIME_DIR:$$XDG_RUNTIME_DIR \
  -e WAYLAND_DISPLAY=$$WAYLAND_DISPLAY \
  -v /run/user/$$(id -u)/wayland-0:/run/user/$$(id -u)/wayland-0 \
  img2text:latest --clip
