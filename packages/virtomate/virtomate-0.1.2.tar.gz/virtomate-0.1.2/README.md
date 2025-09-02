# Virtomate

Virtomate is a handy command-line application for managing virtual machines with libvirt. It runs on any Unix-like system with Python 3.10 and libvirt 9.0 (or newer) installed.

Accomplish complex tasks like cloning virtual machines with ease:

```
$ virtomate domain-clone --mode linked ubuntu-24.04 my-clone
```

Or run a command on the guest without SSH:

```
$ virtomate -p guest-run ubuntu-24.04 -- apt-get update
{
  "exit_code": 0,
  "signal": null,
  "stderr": null,
  "stderr_truncated": false,
  "stdout": "Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease\nHit:2 http://archive.ubuntu.com/ubuntu noble-updates InRelease\nHit:3 http://archive.ubuntu.com/ubuntu noble-backports InRelease\nHit:4 http://security.ubuntu.com/ubuntu noble-security InRelease\nReading package lists...\n",
  "stdout_truncated": false
}
```

Virtomate's scripting-friendly interface makes automating administrative tasks a breeze. Pipe its JSON output to [jq](https://github.com/jqlang/jq) to extract the information you need and combine it with any other tool. Emptying a storage pool becomes a single line of code:

```
$ virtomate volume-list boot | jq '.[].name' | xargs -i virsh vol-delete {} --pool boot
```

Even if virtual machines are running on a remote host, don't let that stop you. Virtomate can connect to other hosts using [remote URIs](https://libvirt.org/uri.html):

```
$ virtomate -c qemu+ssh://ubuntu@10.0.7.3/system -p domain-list
[
  {
    "name": "ubuntu-24.04",
    "state": "running",
    "uuid": "b901fbbb-1012-495d-a32d-90a8ddaa50a7"
  }
]
```

Learn more at <https://virtomate.org/>.

## Installation

```
$ pipx install virtomate
```

For more installation options, see the [Virtomate documentation](https://virtomate.org/).

## Getting Help

If you need help, please start a [discussion on GitHub](https://github.com/aahlenst/virtomate/discussions).

## Contributing

Please see the [contribution guide](CONTRIBUTING.md).

## Development

### Prerequisites

- [Rye 0.28](https://rye.astral.sh/) or newer
- [Python 3.10](https://www.python.org/) or newer
- [libvirt 9.0](https://libvirt.org/) or newer
- [Packer 1.10](https://www.packer.io/) or newer

To run the complete test suite, including the functional tests, you need a machine with an x86 CPU running Linux. Other operating systems like BSD or macOS might work but have not been tested.

### Preparation

To run the complete test suite, including the functional tests, you have to build a couple of virtual machine images and configure libvirt accordingly. This is an optional step, and you can skip it if you do not want to run the functional tests.

#### Install libvirt, QEMU

Refer to the instructions of the respective Linux distribution:

- [Debian](https://wiki.debian.org/KVM)
- [Fedora](https://docs.fedoraproject.org/en-US/quick-docs/virtualization-getting-started/)
- [Ubuntu](https://help.ubuntu.com/community/KVM/Installation)

Check that the command-line tools `virsh` and `qemu-img` are on `PATH` and working.

#### Create Storage Pools

The test suite expects the presence of the following storage pools:

- `default` in `/var/lib/libvirt/images`
- `nvram` in `/var/lib/libvirt/qemu/nvram`

If they do not exist, you can create them as follows:

```
$ virsh pool-define-as default dir --target /var/lib/libvirt/images
$ virsh pool-autostart default
$ virsh pool-build default
$ virsh pool-start default

$ virsh pool-define-as nvram dir --target /var/lib/libvirt/qemu/nvram
$ virsh pool-autostart nvram
$ virsh pool-build nvram
$ virsh pool-start nvram
```

#### Create Virtual Machine Images

The functional tests require some virtual machine images to run. There are [Packer](https://packer.io/) templates in [packer/](packer/) to create them in a couple of minutes:

```
$ pushd packer
$ packer build simple-bios.pkr.hcl
$ packer build simple-uefi.pkr.hcl
$ popd
```

Packer will save the virtual machine images to `packer/dist`.

Then, import them into libvirt by running:

```
$ sudo ./prepare-pool.sh packer/dist
```

### Create a Build

```
$ rye build
```

This will create a source distribution (`.tar.gz`) and a [wheel](https://packaging.python.org/en/latest/specifications/binary-distribution-format/) (`.whl`) in the folder `dist` of the source root.

### Run the Tests

To run the unit tests, run:

```
$ rye test
```

### Run the Functional Tests

**WARNING**: Running the functional tests can cause **data loss**. The test suite will treat all virtual machines and storage volumes whose names start with `virtomate-` as test artefacts and **delete** them after each test.

To run the functional tests, activate the virtual environment with `source .venv/bin/activate` (on Unix-like operating systems) or `. .\env\Scripts\activate.ps1` on Windows. Then run:

```
$ rye test -- --functional
```

Functional tests require a working libvirt installation with QEMU. See the section [Preparation](#preparation) above.

By default, the functional tests connect to `qemu:///system`. If your local user cannot access `qemu:///system`, adding it to the group `libvirt` is usually sufficient.

To run the functional tests against a different libvirt instance, define the environment variable `LIBVIRT_DEFAULT_URI` accordingly. See [the libvirt documentation on Connection URIs](https://libvirt.org/uri.html) on how to do this.

## License

Virtomate is licensed under the [GNU General Public License, version 2 only](https://spdx.org/licenses/GPL-2.0-only.html).
