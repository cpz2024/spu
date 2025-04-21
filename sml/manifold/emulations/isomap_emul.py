# Copyright 2024 Ant Group Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import time

import jax
import jax.numpy as jnp
import numpy as np
from sklearn.manifold import Isomap

import sml.utils.emulation as emulation
from sml.manifold.isomap import ISOMAP


def emul_cpz(mode: emulation.Mode.MULTIPROCESS):
    try:
        # bandwidth and latency only work for docker mode
        emulator = emulation.Emulator(
            emulation.CLUSTER_ABY3_3PC, mode, bandwidth=300, latency=20
        )
        emulator.up()

        def isomap(
            sX,
            num_samples,
            num_features,
            k,
            num_components,
        ):
            embedding = ISOMAP(
                n_components=num_components,
                n_neighbors=k,
                n_samples=num_samples,
                n_features=num_features,
            )
            X_transformed = embedding.fit_transform(sX)
            return X_transformed

        # Set sample size and dimensions
        num_samples = 150  # Number of samples
        num_features = 4  # Sample dimension
        k = 6  # Number of nearest neighbors
        num_components = 3  # Dimension after dimensionality reduction

        # Generate random input
        seed = int(time.time())
        key = jax.random.PRNGKey(seed)
        X = jax.random.uniform(
            key, shape=(num_samples, num_features), minval=0.0, maxval=1.0
        )

        sX = emulator.seal(X)

        ans = emulator.run(isomap, static_argnums=(1, 2, 3, 4))(
            sX,
            num_samples,
            num_features,
            k,
            num_components,
        )

        # print('ans: \n', ans)

        # # sklearn test
        # embedding = Isomap(n_components=num_components, n_neighbors=k)
        # X_transformed = embedding.fit_transform(X)
        # print('X_transformed: \n', X_transformed)

        # np.testing.assert_allclose(
        #     jnp.abs(X_transformed), jnp.abs(ans), rtol=0, atol=4e-2
        # )

    finally:
        emulator.down()


if __name__ == "__main__":
    emul_cpz(emulation.Mode.MULTIPROCESS)
