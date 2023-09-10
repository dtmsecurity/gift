from gift import Gif
import argparse


def main():
    parser = argparse.ArgumentParser(description='Hide and Recover Files in GIFs')
    parser.add_argument('mode', choices=['hide', 'recover', 'analyze', 'spread', 'gather'],
                        help='Mode of operation: "hide" to hide files inside a GIF or "recover" to extract them.')
    parser.add_argument('--source', type=str, help='Path to the source GIF file.', required=False)
    parser.add_argument('--dest', type=str, help='Path to the destination GIF file.', required=False)
    parser.add_argument('filenames', type=str, nargs='+',
                        help='Arbitrary list of filenames to hide or recover based on the mode.')
    args = parser.parse_args()

    if args.mode == 'hide':
        if not args.source:
            parser.error('The --source argument is required for "hide" mode.')
        if not args.dest:
            parser.error('The --dest argument is required for "hide" mode.')
        hide_files(args.source, args.dest, args.filenames)
    elif args.mode == 'recover':
        if not args.source:
            parser.error('The --source argument is required for "hide" mode.')
        recover_files(args.source, args.filenames)
    elif args.mode == 'analyze':
        analyze(args.filenames[0])
    elif args.mode == 'spread':
        if not args.source:
            parser.error('The --source argument is required for "spread" mode.')
        if not args.dest:
            parser.error('The --dest argument is required for "spread" mode.')
        spread_data(args.source, args.dest, args.filenames)
    elif args.mode == 'gather':
        if not args.source:
            parser.error('The --source argument is required for "gather" mode.')
        gather_data(args.source, args.filenames)


def hide_files(source_gif, destination_gif, filenames):
    print(f'Hiding files in {source_gif} and writing to {destination_gif}')
    payloads = []
    for filename in filenames:
        print(f"We will hide: {filename}")
        with open(filename, "rb") as fh:
            payload = fh.read()
            payloads.append(payload)
    with open(source_gif, "rb") as fh, open(destination_gif, "wb") as oh:
        print("Doing magic...")
        g = Gif(file_handle=fh, hide=True, blobs=payloads)
        print(f"Done...now writing to {destination_gif}")
        oh.write(g.buffer)


def recover_files(source_gif, filenames):
    print(f'Recovering files from {source_gif}')
    with open(source_gif, "rb") as fh:
        g = Gif(file_handle=fh, recover=True)
    output_file_index = 0
    for filename in filenames:
        print(f'Recovering {filename}')
        if len(g.blobs) > output_file_index:
            with open(filename, "wb") as oh:
                oh.write(g.blobs[output_file_index])
        else:
            print(f"We don't have that many recovered blobs")
        output_file_index += 1


def analyze(gif_file):
    with open(gif_file, "rb") as fh:
        g = Gif(file_handle=fh)
        print("---")
        print("GIF INFO")
        print("---")
        print(f"header = {g.header.decode()}")
        print(f"frames = {g.frames}")
        print("---")
        print("LOGICAL SCREEN DESCRIPTOR")
        print("---")
        for attr, value in vars(g.LogicalScreenDescriptor).items():
            if not callable(value) and not attr.startswith("__"):
                print(f"{attr} = {value}")
        print("---")
        print("GLOBAL COLOR TABLE")
        print("---")
        for attr, value in vars(g.GlobalColorTable).items():
            if not callable(value) and not attr.startswith("__"):
                print(f"{attr} = {value}")
        print("---")
        print("APPLICATION EXTENSIONS")
        print("---")
        for application_extension in g.application_extensions:
            for attr, value in vars(application_extension).items():
                if not callable(value) and not attr.startswith("__"):
                    if attr == "sub_blocks":
                        for sub_block in value:
                            print(f"sub_block_size: {sub_block.sub_block_size}")
                            print(f"sub_block_data: {sub_block.sub_block_data}")
                    else:
                        print(f"{attr} = {value}")
            print("---")
        print("---")
        print("IMAGE DESCRIPTORS")
        print("---")
        for image_descriptor in g.frame_image_descriptors:
            for attr, value in vars(image_descriptor).items():
                if not callable(value) and not attr.startswith("__"):
                    print(f"{attr} = {value}")
            print("---")
        print("---")
        print("DUMP FRAMES")
        print("---")
        g.render_images()


def split_bytearray(data, num_chunks):
    chunk_size, remainder = divmod(len(data), num_chunks)
    sizes = [chunk_size + (1 if i < remainder else 0) for i in range(num_chunks)]
    chunks = []
    start = 0
    for size in sizes:
        chunks.append(data[start:start + size])
        start += size

    return chunks


def spread_data(source_gif, destination_gif, filenames):
    print(f'Hiding file across frames of {source_gif} and writing to {destination_gif}')
    payloads = []
    filename = filenames[0]
    print(f"We will hide: {filename}")
    with open(filename, "rb") as fh:
        payload = fh.read()

    with open(source_gif, "rb") as fh:
        gif_info = Gif(file_handle=fh)
        number_frames = gif_info.frames
        payloads = split_bytearray(payload, number_frames)
    print(f"We have split {filename} into {len(payloads)}")
    for chunk in payloads:
        print(f"Chunk of size {len(chunk)}")
    with open(source_gif, "rb") as fh, open(destination_gif, "wb") as oh:
        print("Doing magic...")
        g = Gif(file_handle=fh, hide=True, blobs=payloads)
        print(f"Done...now writing to {destination_gif}")
        oh.write(g.buffer)


def gather_data(source_gif, filenames):
    print(f'Recovering files from {source_gif}')
    with open(source_gif, "rb") as fh:
        g = Gif(file_handle=fh, recover=True)
    output_filename = filenames[0]
    print(f'Recovering {output_filename}')
    with open(output_filename, "wb") as oh:
        for blob in g.blobs:
            print(f"Writing recovered blob of size {len(blob)} to {output_filename}")
            oh.write(blob)


if __name__ == '__main__':
    main()