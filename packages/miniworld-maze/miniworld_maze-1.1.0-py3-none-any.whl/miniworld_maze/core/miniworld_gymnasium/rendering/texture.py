"""Texture management for MiniWorld environments."""

import os

import pyglet
from pyglet.gl import *

from ..utils import get_file_path


class Texture:
    """
    Manage the loading and caching of textures, as well as texture randomization
    """

    # List of textures available for a given path
    tex_paths = {}

    # Cache of textures
    tex_cache = {}

    @classmethod
    def get(self, tex_name, rng=None):
        """
        Load a texture by name (or used a cached version)
        Also performs domain randomization if multiple versions are available.
        """

        paths = self.tex_paths.get(tex_name, [])

        # Get an inventory of the existing texture files
        if len(paths) == 0:
            for i in range(1, 10):
                path = get_file_path("textures", "%s_%d" % (tex_name, i), "png")

                if not os.path.exists(path):
                    break
                paths.append(path)

        assert len(paths) > 0, 'failed to load textures for name "%s"' % tex_name

        # If domain-randomization is to be used
        if rng:
            path_idx = rng.int(0, len(paths))
            path = paths[path_idx]
        else:
            path = paths[0]

        if path not in self.tex_cache:
            self.tex_cache[path] = Texture(Texture.load(path), tex_name)

        return self.tex_cache[path]

    @classmethod
    def load(cls, tex_path):
        """
        Load a texture based on its path. No domain randomization.
        In mose cases, this method should not be used directly.
        """

        # print('Loading texture "%s"' % tex_path)

        img = pyglet.image.load(tex_path)
        tex = img.get_texture()
        glEnable(tex.target)
        glBindTexture(tex.target, tex.id)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGB,
            img.width,
            img.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img.get_image_data().get_data("RGBA", img.width * 4),
        )

        # Generate mipmaps (multiple levels of detail)
        glHint(GL_GENERATE_MIPMAP_HINT, GL_NICEST)
        glGenerateMipmap(GL_TEXTURE_2D)

        # Trilinear texture filtering
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

        # Unbind the texture
        glBindTexture(GL_TEXTURE_2D, 0)

        return tex

    def __init__(self, tex, tex_name):
        assert not isinstance(tex, str)
        self.tex = tex
        self.width = self.tex.width
        self.height = self.tex.height
        self.name = tex_name

    def bind(self):
        glBindTexture(self.tex.target, self.tex.id)
