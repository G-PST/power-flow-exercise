/**
 * Copyright (c) 2022, RTE (http://www.rte-france.com)
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */
package com.powsybl.benchmark;

import com.powsybl.iidm.network.Network;
import org.openjdk.jmh.annotations.Level;
import org.openjdk.jmh.annotations.Scope;
import org.openjdk.jmh.annotations.Setup;
import org.openjdk.jmh.annotations.State;

/**
 * @author Geoffroy Jamgotchian <geoffroy.jamgotchian at rte-france.com>
 */
@State(Scope.Thread)
public abstract class AbstractMatpowerNetworkState {

    private Network network;

    @Setup(Level.Trial)
    public void doSetup() {
        network = MatpowerUtil.importMat(getName());
    }

    protected abstract String getName();

    public Network getNetwork() {
        return network;
    }
}
